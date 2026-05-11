"""
moo_viewer.data
~~~~~~~~~~~~~~~
File discovery and cached data loaders.
All loaders return empty DataFrames on missing files — callers
decide how to surface errors to the user.
"""

from __future__ import annotations

import math
import os

import pandas as pd
import streamlit as st


# ─── Folder discovery ─────────────────────────────────────────────────────────

def discover_runs(path: str, case: str) -> list[dict]:
    """Return a list of dicts {folder, cap, rho} for every matching run folder."""
    runs: list[dict] = []
    try:
        entries = os.listdir(path)
    except (FileNotFoundError, PermissionError):
        return runs

    for name in entries:
        if not name.startswith(case):
            continue
        if not os.path.isdir(os.path.join(path, name)):
            continue
        parts = name.split("_")
        try:
            cap = float(parts[-2])
            rho = float(parts[-1])
        except (ValueError, IndexError):
            continue
        runs.append({"folder": name, "cap": cap, "rho": rho})

    return runs


def _csv(path: str, folder: str, filename: str, **kwargs) -> pd.DataFrame | None:
    fp = os.path.join(path, folder, f"{filename}.csv")
    if not os.path.exists(fp):
        return None
    return pd.read_csv(fp, **kwargs)


# ─── Cached loaders ───────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Loading Pareto data…")
def load_pareto(path: str, case: str) -> pd.DataFrame:
    runs = discover_runs(path, case)
    records: list[dict] = []
    for r in runs:
        df = _csv(path, r["folder"], "total_cost")
        if df is None:
            continue
        sec_col = "obs_sec" if "obs_sec" in df.columns else "obj_sec"
        records.append(
            {
                "rho": r["rho"],
                "cap": r["cap"],
                "obj_cost": df.at[0, "obj_cost"],
                "obj_sec": df.at[0, sec_col],
            }
        )
    return pd.DataFrame(records).sort_values("rho") if records else pd.DataFrame()


@st.cache_data(show_spinner="Loading capacity data…")
def load_capacity(path: str, case: str) -> pd.DataFrame:
    runs = discover_runs(path, case)
    dfs: list[pd.DataFrame] = []
    for r in runs:
        df = _csv(path, r["folder"], "cap_inst", usecols=["x1", "y"])
        if df is None:
            continue
        df = df.rename(columns={"x1": "techs", "y": "values"})
        agg = df.groupby("techs", as_index=False)["values"].mean()
        agg["rho"] = r["rho"]
        agg["cap"] = r["cap"]
        dfs.append(agg)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


@st.cache_data(show_spinner="Loading curtailment data…")
def load_curtailment(path: str, case: str) -> pd.DataFrame:
    runs = discover_runs(path, case)
    dfs: list[pd.DataFrame] = []
    for r in runs:
        df = _csv(path, r["folder"], "curtailment", usecols=["x1", "y"])
        if df is None:
            continue
        df = df.rename(columns={"x1": "techs", "y": "values"})
        agg = df.groupby("techs", as_index=False)["values"].sum()
        agg["rho"] = r["rho"]
        agg["cap"] = r["cap"]
        dfs.append(agg)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


@st.cache_data(show_spinner="Loading generation data…")
def load_generation(path: str, case: str) -> pd.DataFrame:
    runs = discover_runs(path, case)
    dfs: list[pd.DataFrame] = []
    for r in runs:
        df = _csv(path, r["folder"], "flow_out", usecols=["x1", "y", "x2", "x3"])
        if df is None:
            continue
        df = df.rename(columns={"x1": "techs", "x2": "hour", "x3": "carrier", "y": "values"})
        df["hour"] = df["hour"].astype(str).str.split("-t").str[-1].astype(int)
        df["rho"] = r["rho"]
        df["cap"] = r["cap"]
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
