"""Generation plots — hourly area chart grid and summed stacked bars."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from moo_viewer.constants import TECH_COLORS
from moo_viewer.plots.bars import _stacked_bars


def _sort_techs(df: pd.DataFrame) -> list[str]:
    """Return techs sorted ascending by total output, excluding zero-sum techs."""
    totals = df.groupby("techs")["values"].sum()
    return totals[totals != 0].sort_values().index.tolist()


def _merge_sink(gen: pd.DataFrame, sink: pd.DataFrame, carrier: str) -> pd.DataFrame:
    """
    Append sink rows to generation, restricted to (cap, rho) pairs already
    present in gen so sink never introduces phantom subplots.
    """
    if sink is None or sink.empty:
        return gen

    existing_pairs = set(zip(gen["cap"], gen["rho"]))

    sink_sub = sink[sink["carrier"] == carrier].copy()
    sink_sub = sink_sub[
        sink_sub.apply(lambda r: (r["cap"], r["rho"]) in existing_pairs, axis=1)
    ]

    if sink_sub.empty:
        return gen

    return pd.concat([gen, sink_sub], ignore_index=True)


def build_hourly(
    result: pd.DataFrame,
    carrier: str,
    sink: pd.DataFrame | None = None,
) -> go.Figure:
    """
    Stacked area grid: rows = emission caps, columns = rho values.
    Each row has a bold cap header; each cell has a rho subtitle.
    Sink surplus (Spillage) and deficit (ENS) are overlaid where present.
    """
    if result.empty:
        return go.Figure()

    gen = result[result["carrier"] == carrier].copy()
    sub = _merge_sink(gen, sink, carrier)

    caps = sorted(sub["cap"].unique())
    rohs = sorted(sub["rho"].unique())
    n_rows, n_cols = len(caps), len(rohs)
    v_spacing = 0.20

    subplot_titles = [
        f"ρ={rho}" if i == 0 else ""
        for i in range(n_rows)
        for rho in rohs
    ]

    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=subplot_titles,
        shared_xaxes=True,
        vertical_spacing=v_spacing,
        horizontal_spacing=0.04,
    )

    # ── per-row cap header annotations ──────────────────────────────────────
    # cap_annotations = []
    # for row_idx, cap in enumerate(caps):
    #     y_paper = 1.0 - row_idx * (1.0 / n_rows) + 0.01
    #     cap_annotations.append(dict(
    #         text=f"<b>Emission cap {int(cap)} %</b>",
    #         x=0.5, y=y_paper,
    #         xref="paper", yref="paper",
    #         xanchor="center", yanchor="bottom",
    #         showarrow=False,
    #         font=dict(size=14),
    #         bgcolor="rgba(240,240,240,0.6)",
    #         borderpad=3,
    #     ))

    # ── traces ───────────────────────────────────────────────────────────────
    shown: set[str] = set()
    for row, cap in enumerate(caps, start=1):
        df_cap = sub[sub["cap"] == cap]
        tech_list = _sort_techs(df_cap)
        for col, rho in enumerate(rohs, start=1):
            df_rho = df_cap[df_cap["rho"] == rho]
            for tech in tech_list:
                df_t = df_rho[df_rho["techs"] == tech]
                if df_t.empty or df_t["values"].sum() == 0:
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
                        hovertemplate=f"{tech}<br>Hour=%{{x}}<br>Value=%{{y:.1f}}<extra></extra>",
                    ),
                    row=row, col=col,
                )
        #fig.update_yaxes(title_text="Output", row=row, col=1)
        fig.update_yaxes(title_text=f"Cap {int(cap)} %", row=row, col=1)

    fig.update_layout(
        annotations=list(fig.layout.annotations), #+ cap_annotations,
        height=340 * max(n_rows, 1),
        legend_title="Technology",
        margin=dict(t=80),
    )
    fig.update_xaxes(title_text="Hour")
    return fig


def build_summed(
    result: pd.DataFrame,
    carrier: str,
    sink: pd.DataFrame | None = None,
) -> go.Figure:
    """Aggregate hourly → total per (tech, rho, cap) then delegate to stacked bars."""
    if result.empty:
        return go.Figure()

    gen = result[result["carrier"] == carrier].copy()
    sub = _merge_sink(gen, sink, carrier)

    # Drop zero-sum techs before aggregating
    active = sub.groupby("techs")["values"].sum()
    active = active[active != 0].index
    sub = sub[sub["techs"].isin(active)]

    df_sum = sub.groupby(["techs", "rho", "cap"], as_index=False)["values"].sum()
    return _stacked_bars(df_sum, f"{carrier} Generation")