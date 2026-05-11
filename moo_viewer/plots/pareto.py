"""Pareto front scatter plot."""

from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go

from moo_viewer.constants import PARETO_NORM_C


def build(df: pd.DataFrame, normalize: bool = False) -> go.Figure:
    """
    Parameters
    ----------
    df:        Output of data.load_pareto().
    normalize: Apply the same normalisation as the original notebook.
    """
    if df.empty:
        return go.Figure()

    plot_df = df.copy()
    plot_df[["obj_cost", "obj_sec"]] *= -1

    if normalize:
        plot_df["obj_cost"] = plot_df["obj_cost"] / plot_df.groupby("cap")["obj_cost"].transform("max")
        plot_df["obj_sec"] = plot_df["obj_sec"] / PARETO_NORM_C

    fig = go.Figure()
    for cap in sorted(plot_df["cap"].unique()):
        sub = plot_df[plot_df["cap"] == cap].sort_values("rho")
        fig.add_trace(
            go.Scatter(
                x=sub["obj_cost"],
                y=sub["obj_sec"],
                mode="markers+lines",
                name=f"Cap {int(cap)} %",
                marker=dict(size=9),
                customdata=sub[["rho"]],
                hovertemplate=(
                    "ρ=%{customdata[0]:.2f}<br>"
                    "Cost=%{x:.4f}<br>"
                    "Social=%{y:.4f}<extra></extra>"
                ),
            )
        )

    suffix = " (normalised)" if normalize else ""
    fig.update_layout(
        xaxis_title=f"Cost Objective{suffix}",
        yaxis_title=f"Social Objective{suffix}",
        legend_title="Emission cap",
        height=560,
    )
    return fig
