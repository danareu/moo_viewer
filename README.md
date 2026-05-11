# moo-viewer

Streamlit dashboard for visualising multi-objective optimisation results.

## Installation

```bash
pip install -e .
```

Or without installing:

```bash
pip install streamlit plotly pandas
streamlit run app.py
```

## Usage

```bash
# After installing
moo-viewer

# Or directly
streamlit run app.py
```

Then in the sidebar:
1. Enter the **results path** (e.g. `/path/to/results/`)
2. Enter the **case prefix** (e.g. `case_social`)
3. Pick a plot from the dropdown

## Expected folder structure

```
results/
  case_social_50_0.0/
    total_cost.csv
    cap_inst.csv
    curtailment.csv
    flow_out.csv
  case_social_50_0.1/
    ...
```

Folder names must follow the pattern `<case>_<cap>_<rho>`.

## Package layout

```
moo_viewer/
  __init__.py       # version
  __main__.py       # CLI entry point
  constants.py      # tech colours, plot list
  data.py           # file discovery + cached loaders
  sidebar.py        # Streamlit sidebar widget
  views.py          # one render_*() per plot type
  plots/
    pareto.py       # Pareto front scatter
    bars.py         # capacity & curtailment stacked bars
    generation.py   # hourly area grid + summed bars
app.py              # thin Streamlit entry point
pyproject.toml
```

## Adding a new plot

1. Add a builder function in `moo_viewer/plots/`.
2. Add a loader in `moo_viewer/data.py` if needed.
3. Add a `render_*()` function in `moo_viewer/views.py`.
4. Add the plot name to `PLOT_OPTIONS` in `moo_viewer/constants.py`.
5. Wire it up in `app.py`.
