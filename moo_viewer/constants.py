TECH_COLORS: dict[str, str] = {
    "n_DG":            "#FF6B35",
    "n_DieselBoiler":  "#C0392B",
    "n_ElectricBoiler":"#3498DB",
    "n_NH3_G":         "#8E44AD",
    "n_PV_ground":     "#F1C40F",
    "n_PV_roof":       "#F39C12",
    "n_WT":            "#27AE60",
    "n_WasteHeat":     "#E67E22",
    "n_Battery":       "#2ECC71",
}

PLOT_OPTIONS: list[str] = [
    "Pareto Front",
    "Installed Capacity",
    "Curtailment",
    "Power Generation (Hourly)",
    "Heat Generation (Hourly)",
    "Power Generation (Yearly)",
    "Heat Generation (Yearly)",
]

# Normalisation constant used in ParetoFront notebook
PARETO_NORM_C: float = 1.2747  # sqrt(sum of squared distances used in original notebook
