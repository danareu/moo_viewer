"""
moo_viewer.sidebar
~~~~~~~~~~~~~~~~~~
Renders the Streamlit sidebar and returns a config dict consumed by the main app.
Uses a tkinter folder-picker dialog so the user never has to type a path.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog

import streamlit as st

from moo_viewer.constants import PLOT_OPTIONS
from moo_viewer.data import discover_runs


def _pick_folder() -> str:
    """Open a native OS folder-picker dialog and return the selected path."""
    root = tk.Tk()
    root.withdraw()          # hide the empty Tk window
    root.wm_attributes("-topmost", True)   # dialog appears on top
    folder = filedialog.askdirectory(title="Select results folder")
    root.destroy()
    return folder or ""


def render() -> dict:
    """
    Draw the sidebar widgets and return a config dict with keys:
        path, case, selected_plot, normalize, cap_filter
    """
    with st.sidebar:
        st.title("⚡ MOO Results Viewer")
        st.markdown("---")
        st.subheader("📁 Data source")

        # ── folder picker ─────────────────────────────────────────────────────
        if "results_path" not in st.session_state:
            st.session_state.results_path = ""

        col1, col2 = st.columns([3, 1])
        with col1:
            # Show the current path (read-only feel, but still editable as fallback)
            st.session_state.results_path = st.text_input(
                "Results path",
                value=st.session_state.results_path,
                placeholder="Click 📂 to browse…",
                label_visibility="collapsed",
            )
        with col2:
            if st.button("📂", help="Browse for results folder"):
                picked = _pick_folder()
                if picked:
                    st.session_state.results_path = picked
                    st.rerun()

        path = st.session_state.results_path

        if path:
            st.caption(f"`{path}`")

        case = st.text_input("Case prefix", placeholder="case_social")

        # ── run discovery ─────────────────────────────────────────────────────
        runs: list[dict] = []
        if path and case:
            runs = discover_runs(path, case)
            st.markdown("---")
            if runs:
                caps_found = sorted({r["cap"] for r in runs})
                rohs_found = sorted({r["rho"] for r in runs})
                st.success(f"Found **{len(runs)}** runs")
                st.markdown(f"- **Caps:** {[int(c) for c in caps_found]}")
                st.markdown(f"- **ρ values:** {[round(r, 2) for r in rohs_found]}")
            else:
                st.warning("No matching folders found. Check path and case prefix.")

        st.markdown("---")
        selected_plot = st.selectbox("📊 Select plot", PLOT_OPTIONS)

        # ── plot-specific controls ────────────────────────────────────────────
        normalize = False
        if selected_plot == "Pareto Front":
            normalize = st.checkbox("Normalize objectives", value=False)

        cap_filter = "All"
        if selected_plot in ("Power Generation (Hourly)", "Heat Generation (Hourly)"):
            st.info("Hourly plots can be large — filter by cap to speed up rendering.")
            cap_options = ["All"] + sorted({str(int(r["cap"])) for r in runs})
            cap_filter = st.selectbox("Filter by emission cap", cap_options)

        st.markdown("---")
        if st.button("🔄 Clear cache"):
            st.cache_data.clear()
            st.rerun()

    return {
        "path": path,
        "case": case,
        "selected_plot": selected_plot,
        "normalize": normalize,
        "cap_filter": cap_filter,
        "runs": runs,
    }
