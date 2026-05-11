"""
moo_viewer.views
~~~~~~~~~~~~~~~~
One render_*() function per plot type.  Each function loads its data,
builds the figure, and displays it — keeping app.py thin.
"""

from __future__ import annotations

import streamlit as st

from moo_viewer import data
from moo_viewer.plots import bars, generation, pareto


def _warn_empty(name: str) -> None:
    st.warning(f"Could not load `{name}` from any run folder. Check the file exists.")


def render_pareto(path: str, case: str, normalize: bool) -> None:
    df = data.load_pareto(path, case)
    if df.empty:
        _warn_empty("total_cost.csv")
        return
    fig = pareto.build(df, normalize=normalize)
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Raw data"):
        st.dataframe(df)


def render_capacity(path: str, case: str) -> None:
    df = data.load_capacity(path, case)
    if df.empty:
        _warn_empty("cap_inst.csv")
        return
    fig = bars.build_capacity(df)
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Raw data"):
        st.dataframe(df)


def render_curtailment(path: str, case: str) -> None:
    df = data.load_curtailment(path, case)
    if df.empty:
        _warn_empty("curtailment.csv")
        return
    fig = bars.build_curtailment(df)
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Raw data"):
        st.dataframe(df)


def render_generation_hourly(path: str, case: str, carrier: str, cap_filter: str) -> None:
    df   = data.load_generation(path, case)
    sink = data.load_sink(path, case)
    if df.empty:
        _warn_empty("flow_out.csv")
        return
    if cap_filter != "All":
        df   = df[df["cap"]   == float(cap_filter)]
        sink = sink[sink["cap"] == float(cap_filter)] if not sink.empty else sink
    with st.spinner("Rendering hourly chart…"):
        fig = generation.build_hourly(df, carrier, sink=sink)
    st.plotly_chart(fig, use_container_width=True)


def render_generation_summed(path: str, case: str, carrier: str) -> None:
    df   = data.load_generation(path, case)
    sink = data.load_sink(path, case)
    if df.empty:
        _warn_empty("flow_out.csv")
        return
    fig = generation.build_summed(df, carrier, sink=sink)
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Raw data"):
        agg = (
            df[df["carrier"] == carrier]
            .groupby(["techs", "rho", "cap"], as_index=False)["values"]
            .sum()
        )
        st.dataframe(agg)
