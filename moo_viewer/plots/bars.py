"""Installed-capacity and curtailment stacked-bar plots."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from moo_viewer.constants import TECH_COLORS


def _stacked_bars(result: pd.DataFrame, title_prefix: str) -> go.Figure:
    """Generic stacked-bar subplots: one subplot per emission cap, x-axis = ρ."""
    caps = sorted(result["cap"].unique())
    fig = make_subplots(
        rows=len(caps),
        cols=1,
        subplot_titles=[f"{title_prefix} — Emission cap {int(c)} %" for c in caps],
        vertical_spacing=0.12,
    )
    shown: set[str] = set()
    for row, cap in enumerate(caps, start=1):
        df_cap = result[result["cap"] == cap]
        techs = [t for t in TECH_COLORS if t in df_cap["techs"].unique()]
        for tech in techs:
            agg = (
                df_cap[df_cap["techs"] == tech]
                .groupby("rho")["values"]
                .sum()
                .reset_index()
            )
            sl = tech not in shown
            shown.add(tech)
            fig.add_trace(
                go.Bar(
                    x=agg["rho"],
                    y=agg["values"],
                    name=tech,
                    marker_color=TECH_COLORS[tech],
                    legendgroup=tech,
                    showlegend=sl,
                    hovertemplate=f"{tech}<br>ρ=%{{x:.2f}}<br>Value=%{{y:.2f}}<extra></extra>",
                ),
                row=row,
                col=1,
            )
    fig.update_layout(
        barmode="stack",
        height=420 * len(caps),
        legend_title="Technology",
        margin=dict(t=60),
    )
    fig.update_xaxes(tickmode="linear", tick0=0, dtick=0.1, title_text="ρ")
    return fig


def build_capacity(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    return _stacked_bars(df, "Installed Capacity (GW)")


def build_curtailment(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    return _stacked_bars(df, "Curtailment (GWh)")
