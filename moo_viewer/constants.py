TECH_COLORS: dict[str, str] = {
    # generators
    "n_DG":             "#FF6B35",
    "n_DieselBoiler":   "#C0392B",
    "n_ElectricBoiler": "#3498DB",
    "n_NH3_G":          "#8E44AD",
    "n_PV_ground":      "#F1C40F",
    "n_PV_roof":        "#F39C12",
    "n_WT":             "#27AE60",
    "n_WasteHeat":      "#E67E22",
    "n_Battery":        "#2ECC71",
    # sink-derived traces
    "ENS (Power)":      "#E74C3C",
    "ENS (Heat)":       "#922B21",
    "Spillage (Power)": "#85C1E9",
    "Spillage (Heat)":  "#A9CCE3",
    "ENS (Waste Heat)": "#F0B27A",
    "Spillage (Waste Heat)": "#D5DBDB",
}

# Maps substrings found in sink tech names → human-readable carrier label
SINK_CARRIER_MAP: dict[str, str] = {
    "Power":      "Power",
    "Heat":       "Heat",
    "Waste_Heat": "Waste Heat",
    "WasteHeat":  "Waste Heat",
}

PLOT_OPTIONS: list[str] = [
    "Pareto Front",
    "Installed Capacity",
    "Curtailment",
    "Power Generation (Hourly)",
    "Heat Generation (Hourly)",
    "Power Generation (Summed by ρ)",
    "Heat Generation (Summed by ρ)",
]

# Normalisation constant used in ParetoFront notebook
PARETO_NORM_C: float = 1.2747
