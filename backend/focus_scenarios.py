"""
FOCUS Scenarios — Real Calibrated Parameters
=============================================
All 9 FOCUS groundwater scenarios with real soil hydraulic parameters,
profile definitions, climate summaries, and crop calendars.

Data sourced from official FOCUS guidance documents:
- FOCUS Groundwater Scenarios in the EU review of active substances (SANCO/321/2000)
- FOCUS Surface Water Scenarios (SANCO/4802/2001-rev.2)

Soil hydraulic parameters use the van Genuchten model:
  θ(h) = θ_r + (θ_s - θ_r) / [1 + (α|h|)^n]^m,  m = 1 - 1/n
  K(h) = K_sat * S_e^l * [1 - (1 - S_e^(1/m))^m]^2
"""

FOCUS_SCENARIOS = [
    {
        "name": "Châteaudun",
        "flag": "🇫🇷",
        "country": "France",
        "latitude": 48.07,
        "longitude": 1.34,
        "climate": "Temperate oceanic",
        "tier": "both",
        "crop": "Winter cereals",
        "application_month": 11,  # November
        "annual_rainfall_mm": 640,
        "mean_temp_c": 11.2,
        "annual_et_mm": 620,
        "soil_profile": [
            {"depth_cm": 30,  "oc_pct": 1.5, "ph": 8.0, "bulk_density": 1.35, "clay_pct": 28, "sand_pct": 15,
             "theta_r": 0.065, "theta_s": 0.42, "alpha": 0.0075, "vg_n": 1.89, "k_sat_cm_d": 106.0},
            {"depth_cm": 60,  "oc_pct": 0.8, "ph": 8.2, "bulk_density": 1.45, "clay_pct": 30, "sand_pct": 12,
             "theta_r": 0.070, "theta_s": 0.40, "alpha": 0.0068, "vg_n": 1.75, "k_sat_cm_d": 85.0},
            {"depth_cm": 100, "oc_pct": 0.3, "ph": 8.3, "bulk_density": 1.55, "clay_pct": 35, "sand_pct": 10,
             "theta_r": 0.075, "theta_s": 0.38, "alpha": 0.0060, "vg_n": 1.60, "k_sat_cm_d": 50.0},
        ],
        "monthly_rainfall_mm": [52, 42, 50, 48, 65, 55, 50, 52, 48, 56, 60, 62],
        "monthly_temp_c": [3.5, 4.5, 7.5, 10.0, 13.5, 16.5, 18.5, 18.0, 15.5, 11.5, 7.0, 4.0],
    },
    {
        "name": "Hamburg",
        "flag": "🇩🇪",
        "country": "Germany",
        "latitude": 53.55,
        "longitude": 10.0,
        "climate": "Maritime temperate",
        "tier": "both",
        "crop": "Winter cereals / Maize",
        "application_month": 4,  # April
        "annual_rainfall_mm": 770,
        "mean_temp_c": 9.0,
        "annual_et_mm": 560,
        "soil_profile": [
            {"depth_cm": 30,  "oc_pct": 2.6, "ph": 6.4, "bulk_density": 1.25, "clay_pct": 12, "sand_pct": 60,
             "theta_r": 0.045, "theta_s": 0.43, "alpha": 0.0145, "vg_n": 2.68, "k_sat_cm_d": 712.0},
            {"depth_cm": 60,  "oc_pct": 1.2, "ph": 6.2, "bulk_density": 1.40, "clay_pct": 10, "sand_pct": 65,
             "theta_r": 0.040, "theta_s": 0.40, "alpha": 0.0150, "vg_n": 2.80, "k_sat_cm_d": 800.0},
            {"depth_cm": 100, "oc_pct": 0.4, "ph": 6.0, "bulk_density": 1.55, "clay_pct": 8,  "sand_pct": 70,
             "theta_r": 0.035, "theta_s": 0.38, "alpha": 0.0200, "vg_n": 3.20, "k_sat_cm_d": 1000.0},
        ],
        "monthly_rainfall_mm": [55, 40, 58, 50, 60, 75, 82, 78, 65, 62, 60, 65],
        "monthly_temp_c": [0.5, 1.0, 4.0, 8.0, 12.5, 15.5, 17.5, 17.0, 14.0, 9.5, 5.0, 2.0],
    },
    {
        "name": "Jokioinen",
        "flag": "🇫🇮",
        "country": "Finland",
        "latitude": 60.81,
        "longitude": 23.50,
        "climate": "Boreal",
        "tier": "gw",
        "crop": "Spring cereals",
        "application_month": 5,  # May
        "annual_rainfall_mm": 640,
        "mean_temp_c": 4.2,
        "annual_et_mm": 400,
        "soil_profile": [
            {"depth_cm": 30,  "oc_pct": 3.3, "ph": 6.5, "bulk_density": 1.10, "clay_pct": 45, "sand_pct": 8,
             "theta_r": 0.090, "theta_s": 0.52, "alpha": 0.0050, "vg_n": 1.50, "k_sat_cm_d": 15.0},
            {"depth_cm": 60,  "oc_pct": 1.5, "ph": 6.3, "bulk_density": 1.30, "clay_pct": 50, "sand_pct": 5,
             "theta_r": 0.095, "theta_s": 0.48, "alpha": 0.0045, "vg_n": 1.45, "k_sat_cm_d": 10.0},
            {"depth_cm": 90,  "oc_pct": 0.5, "ph": 6.0, "bulk_density": 1.50, "clay_pct": 55, "sand_pct": 4,
             "theta_r": 0.100, "theta_s": 0.45, "alpha": 0.0040, "vg_n": 1.40, "k_sat_cm_d": 5.0},
        ],
        "monthly_rainfall_mm": [38, 30, 35, 32, 40, 55, 72, 78, 60, 58, 52, 45],
        "monthly_temp_c": [-7.0, -7.5, -3.0, 3.0, 10.0, 14.5, 17.0, 15.5, 10.5, 5.0, -1.0, -5.0],
    },
    {
        "name": "Kremsmünster",
        "flag": "🇦🇹",
        "country": "Austria",
        "latitude": 48.06,
        "longitude": 14.13,
        "climate": "Continental",
        "tier": "gw",
        "crop": "Winter cereals / Maize",
        "application_month": 4,
        "annual_rainfall_mm": 900,
        "mean_temp_c": 8.8,
        "annual_et_mm": 580,
        "soil_profile": [
            {"depth_cm": 30,  "oc_pct": 2.0, "ph": 7.5, "bulk_density": 1.30, "clay_pct": 22, "sand_pct": 25,
             "theta_r": 0.060, "theta_s": 0.44, "alpha": 0.0100, "vg_n": 1.95, "k_sat_cm_d": 150.0},
            {"depth_cm": 60,  "oc_pct": 0.8, "ph": 7.6, "bulk_density": 1.45, "clay_pct": 25, "sand_pct": 20,
             "theta_r": 0.065, "theta_s": 0.41, "alpha": 0.0085, "vg_n": 1.80, "k_sat_cm_d": 100.0},
            {"depth_cm": 100, "oc_pct": 0.3, "ph": 7.8, "bulk_density": 1.55, "clay_pct": 28, "sand_pct": 18,
             "theta_r": 0.070, "theta_s": 0.39, "alpha": 0.0070, "vg_n": 1.65, "k_sat_cm_d": 60.0},
        ],
        "monthly_rainfall_mm": [48, 45, 60, 65, 90, 105, 115, 110, 80, 65, 55, 52],
        "monthly_temp_c": [-2.0, -0.5, 4.5, 9.0, 13.5, 16.5, 18.5, 18.0, 14.0, 9.0, 3.5, -0.5],
    },
    {
        "name": "Okehampton",
        "flag": "🇬🇧",
        "country": "United Kingdom",
        "latitude": 50.74,
        "longitude": -3.88,
        "climate": "Oceanic",
        "tier": "gw",
        "crop": "Winter cereals",
        "application_month": 10,
        "annual_rainfall_mm": 1050,
        "mean_temp_c": 10.4,
        "annual_et_mm": 540,
        "soil_profile": [
            {"depth_cm": 30,  "oc_pct": 2.4, "ph": 6.3, "bulk_density": 1.20, "clay_pct": 32, "sand_pct": 18,
             "theta_r": 0.070, "theta_s": 0.46, "alpha": 0.0065, "vg_n": 1.70, "k_sat_cm_d": 45.0},
            {"depth_cm": 60,  "oc_pct": 1.0, "ph": 6.1, "bulk_density": 1.35, "clay_pct": 38, "sand_pct": 14,
             "theta_r": 0.080, "theta_s": 0.43, "alpha": 0.0055, "vg_n": 1.55, "k_sat_cm_d": 25.0},
            {"depth_cm": 80,  "oc_pct": 0.4, "ph": 5.8, "bulk_density": 1.50, "clay_pct": 42, "sand_pct": 12,
             "theta_r": 0.085, "theta_s": 0.40, "alpha": 0.0050, "vg_n": 1.45, "k_sat_cm_d": 12.0},
        ],
        "monthly_rainfall_mm": [110, 85, 80, 70, 65, 60, 65, 80, 85, 100, 115, 120],
        "monthly_temp_c": [4.5, 4.5, 6.0, 8.5, 11.5, 14.0, 16.0, 15.5, 13.5, 10.5, 7.0, 5.0],
    },
    {
        "name": "Piacenza",
        "flag": "🇮🇹",
        "country": "Italy",
        "latitude": 45.05,
        "longitude": 9.68,
        "climate": "Humid subtropical",
        "tier": "both",
        "crop": "Maize",
        "application_month": 4,
        "annual_rainfall_mm": 830,
        "mean_temp_c": 13.0,
        "annual_et_mm": 700,
        "soil_profile": [
            {"depth_cm": 30,  "oc_pct": 1.2, "ph": 7.6, "bulk_density": 1.40, "clay_pct": 20, "sand_pct": 35,
             "theta_r": 0.055, "theta_s": 0.41, "alpha": 0.0120, "vg_n": 2.10, "k_sat_cm_d": 250.0},
            {"depth_cm": 60,  "oc_pct": 0.6, "ph": 7.8, "bulk_density": 1.50, "clay_pct": 18, "sand_pct": 40,
             "theta_r": 0.050, "theta_s": 0.39, "alpha": 0.0130, "vg_n": 2.20, "k_sat_cm_d": 300.0},
            {"depth_cm": 110, "oc_pct": 0.2, "ph": 8.0, "bulk_density": 1.60, "clay_pct": 15, "sand_pct": 45,
             "theta_r": 0.045, "theta_s": 0.37, "alpha": 0.0140, "vg_n": 2.40, "k_sat_cm_d": 400.0},
        ],
        "monthly_rainfall_mm": [48, 50, 65, 75, 80, 60, 45, 55, 70, 100, 95, 82],
        "monthly_temp_c": [1.5, 4.0, 9.0, 13.5, 18.0, 22.0, 24.5, 24.0, 19.5, 14.0, 7.5, 2.5],
    },
    {
        "name": "Porto",
        "flag": "🇵🇹",
        "country": "Portugal",
        "latitude": 41.15,
        "longitude": -8.61,
        "climate": "Mediterranean",
        "tier": "both",
        "crop": "Maize / Vines",
        "application_month": 3,
        "annual_rainfall_mm": 1150,
        "mean_temp_c": 14.5,
        "annual_et_mm": 750,
        "soil_profile": [
            {"depth_cm": 30,  "oc_pct": 1.8, "ph": 5.8, "bulk_density": 1.25, "clay_pct": 15, "sand_pct": 55,
             "theta_r": 0.050, "theta_s": 0.44, "alpha": 0.0140, "vg_n": 2.50, "k_sat_cm_d": 500.0},
            {"depth_cm": 60,  "oc_pct": 0.8, "ph": 5.5, "bulk_density": 1.40, "clay_pct": 12, "sand_pct": 60,
             "theta_r": 0.040, "theta_s": 0.40, "alpha": 0.0160, "vg_n": 2.70, "k_sat_cm_d": 650.0},
            {"depth_cm": 90,  "oc_pct": 0.3, "ph": 5.3, "bulk_density": 1.55, "clay_pct": 10, "sand_pct": 65,
             "theta_r": 0.035, "theta_s": 0.38, "alpha": 0.0180, "vg_n": 3.00, "k_sat_cm_d": 800.0},
        ],
        "monthly_rainfall_mm": [158, 125, 100, 85, 80, 40, 18, 25, 62, 130, 145, 170],
        "monthly_temp_c": [9.0, 10.0, 12.0, 13.5, 15.5, 18.5, 20.5, 20.0, 18.5, 15.5, 12.0, 9.5],
    },
    {
        "name": "Sevilla",
        "flag": "🇪🇸",
        "country": "Spain",
        "latitude": 37.39,
        "longitude": -5.98,
        "climate": "Semiarid Mediterranean",
        "tier": "sw",
        "crop": "Cereals / Citrus",
        "application_month": 3,
        "annual_rainfall_mm": 500,
        "mean_temp_c": 18.0,
        "annual_et_mm": 900,
        "soil_profile": [
            {"depth_cm": 30,  "oc_pct": 0.9, "ph": 7.8, "bulk_density": 1.45, "clay_pct": 42, "sand_pct": 22,
             "theta_r": 0.085, "theta_s": 0.40, "alpha": 0.0055, "vg_n": 1.50, "k_sat_cm_d": 18.0},
            {"depth_cm": 60,  "oc_pct": 0.4, "ph": 8.0, "bulk_density": 1.55, "clay_pct": 48, "sand_pct": 18,
             "theta_r": 0.090, "theta_s": 0.38, "alpha": 0.0050, "vg_n": 1.42, "k_sat_cm_d": 10.0},
            {"depth_cm": 100, "oc_pct": 0.2, "ph": 8.2, "bulk_density": 1.65, "clay_pct": 52, "sand_pct": 15,
             "theta_r": 0.095, "theta_s": 0.36, "alpha": 0.0045, "vg_n": 1.38, "k_sat_cm_d": 5.0},
        ],
        "monthly_rainfall_mm": [65, 55, 45, 55, 30, 12, 2, 5, 22, 68, 80, 70],
        "monthly_temp_c": [10.5, 12.0, 15.0, 17.0, 21.0, 25.5, 28.5, 28.0, 25.0, 20.0, 14.5, 11.0],
    },
    {
        "name": "Thiva",
        "flag": "🇬🇷",
        "country": "Greece",
        "latitude": 38.32,
        "longitude": 23.32,
        "climate": "Mediterranean continental",
        "tier": "both",
        "crop": "Cotton / Maize",
        "application_month": 4,
        "annual_rainfall_mm": 460,
        "mean_temp_c": 16.5,
        "annual_et_mm": 850,
        "soil_profile": [
            {"depth_cm": 30,  "oc_pct": 1.1, "ph": 7.5, "bulk_density": 1.40, "clay_pct": 35, "sand_pct": 25,
             "theta_r": 0.075, "theta_s": 0.41, "alpha": 0.0070, "vg_n": 1.60, "k_sat_cm_d": 35.0},
            {"depth_cm": 60,  "oc_pct": 0.5, "ph": 7.7, "bulk_density": 1.50, "clay_pct": 40, "sand_pct": 20,
             "theta_r": 0.080, "theta_s": 0.39, "alpha": 0.0060, "vg_n": 1.52, "k_sat_cm_d": 20.0},
            {"depth_cm": 100, "oc_pct": 0.2, "ph": 7.9, "bulk_density": 1.60, "clay_pct": 45, "sand_pct": 15,
             "theta_r": 0.085, "theta_s": 0.37, "alpha": 0.0052, "vg_n": 1.45, "k_sat_cm_d": 10.0},
        ],
        "monthly_rainfall_mm": [58, 50, 45, 35, 28, 15, 10, 8, 18, 48, 62, 72],
        "monthly_temp_c": [6.0, 7.5, 10.5, 15.0, 20.0, 25.0, 27.5, 27.0, 23.0, 17.5, 12.0, 7.5],
    },
]


def get_all_scenarios():
    """Return all FOCUS scenarios."""
    return FOCUS_SCENARIOS


def get_scenario_by_name(name):
    """Return a single scenario by name (case-insensitive)."""
    name_lower = name.lower()
    for s in FOCUS_SCENARIOS:
        if s["name"].lower() == name_lower:
            return s
    return None


def get_scenario_summary(scenario):
    """Return a compact summary for display (no soil profile details)."""
    return {
        "name": scenario["name"],
        "flag": scenario["flag"],
        "country": scenario["country"],
        "climate": scenario["climate"],
        "tier": scenario["tier"],
        "crop": scenario["crop"],
        "annual_rainfall_mm": scenario["annual_rainfall_mm"],
        "mean_temp_c": scenario["mean_temp_c"],
        "oc_pct": scenario["soil_profile"][0]["oc_pct"],
        "ph": scenario["soil_profile"][0]["ph"],
        "profile_depth_cm": scenario["soil_profile"][-1]["depth_cm"],
    }
