"""
app.py — Streamlit entrypoint.

Run with:
    streamlit run app.py
"""

import streamlit as st

from moo_viewer import sidebar, views

st.set_page_config(
    page_title="Longyearbyen Results Viewer",
    page_icon="⚡",
    layout="wide",
)

st.title("Longyearbyen's Decarbonization Explorer")

cfg = sidebar.render()
path, case = cfg["path"], cfg["case"]

if not path or not case:
    st.info("👈  Enter a results **path** and **case prefix** in the sidebar to get started.")
    st.stop()

if not cfg["runs"]:
    st.error("No matching run folders found. Check path and case prefix.")
    st.stop()

plot = cfg["selected_plot"]

if plot == "Pareto Front":
    views.render_pareto(path, case, cfg["normalize"])

elif plot == "Installed Capacity":
    views.render_capacity(path, case)

elif plot == "Curtailment":
    views.render_curtailment(path, case)

elif plot in ("Power Generation (Hourly)", "Heat Generation (Hourly)"):
    carrier = "Power" if "Power" in plot else "Heat"
    views.render_generation_hourly(path, case, carrier, cfg["cap_filter"])

elif plot in ("Power Generation (Yearly)", "Heat Generation (Yearly)"):
    carrier = "Power" if "Power" in plot else "Heat"
    views.render_generation_summed(path, case, carrier)

elif plot == "Emissions":
    views.render_emissions(path, case)