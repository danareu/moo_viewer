"""Generation plots — hourly area chart grid and summed stacked bars."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from moo_viewer.constants import TECH_COLORS
from moo_viewer.plots.bars import _stacked_bars


def _sort_techs(df: pd.DataFrame, carrier: str) -> list[str]:
    """Return techs sorted ascending by total output for a given carrier."""
    sub = df[df["carrier"].isin([carrier]) & (df["values"] != 0)]
    return sub.groupby("techs")["values"].sum().sort_values().index.tolist()


def build_hourly(result: pd.DataFrame, carrier: str) -> go.Figure:
    """
    Stacked area grid: rows = emission caps, columns = ρ values.
    Each cell shows hourly generation for the given carrier.
    """
    if result.empty:
        return go.Figure()

    sub = result[result["carrier"] == carrier]
    caps = sorted(sub["cap"].unique())
    rohs = sorted(sub["rho"].unique())

    fig = make_subplots(
        rows=len(caps),
        cols=len(rohs),
        subplot_titles=[f"ρ={rho}" for rho in rohs],
        vertical_spacing=0.08,
        horizontal_spacing=0.04,
    )
    shown: set[str] = set()
    for row, cap in enumerate(caps, start=1):
        df_cap = sub[sub["cap"] == cap]
        tech_list = _sort_techs(df_cap, carrier)
        for col, rho in enumerate(rohs, start=1):
            df_rho = df_cap[df_cap["rho"] == rho]
            for tech in tech_list:
                df_t = df_rho[df_rho["techs"] == tech]
                if df_t.empty:
                    continue
                sl = tech not in shown
                shown.add(tech)
                fig.add_trace(
                    go.Scatter(
                        x=df_t["hour"],
                        y=df_t["values"],
                        name=tech,
                        legendgroup=tech,
                        stackgroup="one",
                        showlegend=sl,
                        line=dict(color=TECH_COLORS.get(tech, "#888")),
                        hovertemplate=(
                            f"{tech}<br>Hour=%{{x}}<br>Value=%{{y:.1f}}<extra></extra>"
                        ),
                    ),
                    row=row,
                    col=col,
                )
        fig.update_yaxes(title_text=f"Cap {int(cap)} %", row=row, col=1)

    fig.update_layout(
        height=200 * max(len(caps), 1),
        width=370 * max(len(rohs), 1),
        legend_title="Technology",
        margin=dict(t=60),
    )
    return fig


def build_summed(result: pd.DataFrame, carrier: str) -> go.Figure:
    """Aggregate hourly → total per (tech, rho, cap) then delegate to stacked bars."""
    if result.empty:
        return go.Figure()

    df_sum = (
        result[result["carrier"] == carrier]
        .groupby(["techs", "rho", "cap"], as_index=False)["values"]
        .sum()
    )
    return _stacked_bars(df_sum, f"{carrier} Generation")
