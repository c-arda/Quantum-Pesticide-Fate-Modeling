"""
Classical Pesticide Fate Model Solver
======================================
Simplified 1D pesticide transport model implementing:
  - Richards equation (unsaturated water flow) — simplified to capacity-based
  - Convection-dispersion equation (solute transport)
  - First-order degradation (DegT50 → rate constant)
  - Linear/Freundlich sorption (Koc × foc)
  - 20-year daily timestep simulation

Produces PEC (Predicted Environmental Concentration) time series
and FOCUS-standard metrics (80th percentile annual max).
"""

import numpy as np


def run_simulation(substance, scenario, years=20, quantum_params=None):
    """
    Run a pesticide fate simulation.

    Parameters
    ----------
    substance : dict
        Substance properties from SPIN database.
    scenario : dict
        FOCUS scenario parameters.
    years : int
        Simulation duration in years.
    quantum_params : dict or None
        If provided, uses quantum-predicted DegT50 and Koc instead of
        experimental values.  Keys: 'degT50_soil', 'koc'.

    Returns
    -------
    dict with:
        - time_days: array of day numbers
        - pec_soil_mg_kg: soil PEC time series (mg/kg)
        - pec_gw_ug_l: groundwater PEC time series (µg/L)
        - leaching_ug_l: leachate concentration at 1m depth
        - annual_max_pec: max PEC per year
        - pec_80th: 80th percentile of annual max PEC (FOCUS metric)
        - total_leached_g_ha: cumulative mass leached
        - mass_balance: final mass balance check
    """

    # ── Extract parameters ──────────────────────────────────────────
    if quantum_params:
        deg_t50 = quantum_params.get("degT50_soil", substance["degT50_soil"])
        koc     = quantum_params.get("koc", substance["koc"])
    else:
        deg_t50 = substance["degT50_soil"]
        koc     = substance["koc"]

    # Ensure positive values
    deg_t50 = max(deg_t50, 0.1)
    koc     = max(koc, 0.1)

    # Degradation rate constant (1/day)
    k_deg = np.log(2) / deg_t50

    # Soil profile (use topsoil for sorption)
    topsoil = scenario["soil_profile"][0]
    foc = topsoil["oc_pct"] / 100.0  # fractional organic carbon
    bulk_density = topsoil["bulk_density"]  # g/cm³
    theta = topsoil["theta_s"] * 0.7  # field capacity ≈ 70% of θ_s
    dispersion_length = 5.0  # cm (typical for field soils)

    # Freundlich sorption
    freundlich_n = substance.get("freundlich_n", 0.9)
    kd = koc * foc  # linear distribution coefficient (mL/g)

    # Retardation factor (dimensionless)
    R = 1 + (bulk_density * kd) / theta

    # ── Spatial discretization ──────────────────────────────────────
    profile_depth = scenario["soil_profile"][-1]["depth_cm"]  # cm
    n_nodes = 50
    dz = profile_depth / n_nodes  # cm
    depths = np.linspace(dz / 2, profile_depth - dz / 2, n_nodes)

    # ── Temporal setup ──────────────────────────────────────────────
    n_days = years * 365
    dt = 1.0  # day

    # Monthly rainfall and temperature
    monthly_rain = np.array(scenario["monthly_rainfall_mm"])  # mm/month
    monthly_temp = np.array(scenario["monthly_temp_c"])
    application_month = scenario.get("application_month", 4)  # default April

    # Application rate (kg/ha = g/m² × 0.1)
    app_rate_kg_ha = 1.0  # standard 1 kg/ha active substance
    app_rate_g_m2 = app_rate_kg_ha * 0.1  # g/m²
    mixing_depth_cm = 5.0  # incorporation depth

    # ── Initialize concentration array ──────────────────────────────
    # conc[j] = mass concentration in soil solution (µg/mL ≈ mg/L) at node j
    conc = np.zeros(n_nodes)

    # ── Output arrays ───────────────────────────────────────────────
    pec_soil = np.zeros(n_days)       # PEC in topsoil (mg/kg)
    pec_gw   = np.zeros(n_days)       # concentration at 1m depth (µg/L)
    leachate = np.zeros(n_days)       # leachate flux (µg/L)

    total_applied = 0.0
    total_degraded = 0.0
    total_leached = 0.0

    # ── Build layered OC profile for depth-dependent degradation ────
    oc_profile = np.zeros(n_nodes)
    for j in range(n_nodes):
        d = depths[j]
        for layer in scenario["soil_profile"]:
            if d <= layer["depth_cm"]:
                oc_profile[j] = layer["oc_pct"] / 100.0
                break
        else:
            oc_profile[j] = scenario["soil_profile"][-1]["oc_pct"] / 100.0

    # Depth-dependent degradation: slower in subsoil
    depth_factor = np.exp(-depths / 30.0)  # exponential decay of microbial activity
    k_deg_profile = k_deg * depth_factor

    # ── Time loop ───────────────────────────────────────────────────
    for day in range(n_days):
        month = (day % 365) // 30  # approximate month (0–11)
        if month > 11:
            month = 11

        # ---- Daily rainfall (mm → cm) ----
        daily_rain_cm = monthly_rain[month] / 30.0 / 10.0  # mm/day → cm/day

        # ET (simple fraction of rainfall, temperature-dependent)
        et_factor = 0.3 + 0.4 * max(0, monthly_temp[month]) / 25.0
        daily_et_cm = daily_rain_cm * et_factor

        # Net infiltration (cm/day)
        q_inf = max(0, daily_rain_cm - daily_et_cm)  # cm/day

        # ---- Temperature-adjusted degradation ----
        temp_factor = np.exp(0.08 * (monthly_temp[month] - 20.0))  # Q10 ≈ 2.2

        # ---- Application ----
        day_of_year = day % 365
        app_day = (application_month - 1) * 30 + 15  # mid-month

        if day_of_year == app_day:
            # Add substance to top mixing_depth_cm
            n_mix = max(1, int(mixing_depth_cm / dz))
            mass_per_node = app_rate_g_m2 * 1e6 / (n_mix * dz * bulk_density * 1000)
            # mass_per_node is in µg/g = mg/kg
            # convert to solution concentration: C_sol = C_total / R
            c_add = mass_per_node / R
            conc[:n_mix] += c_add
            total_applied += app_rate_g_m2 * 1e6  # µg/m²

        # ---- Degradation (first-order, all nodes) ----
        deg_mass = conc * (1 - np.exp(-k_deg_profile * temp_factor * dt)) * R
        conc *= np.exp(-k_deg_profile * temp_factor * dt)
        total_degraded += np.sum(deg_mass) * dz * theta

        # ---- Advection (upwind scheme) ----
        v_pore = q_inf / theta  # pore velocity (cm/day)
        v_eff = v_pore / R      # effective velocity with retardation

        if v_eff > 0:
            courant = v_eff * dt / dz
            if courant > 0.9:
                # Sub-stepping for stability
                n_sub = int(courant / 0.9) + 1
                dt_sub = dt / n_sub
            else:
                n_sub = 1
                dt_sub = dt

            for _ in range(n_sub):
                flux = np.zeros(n_nodes + 1)
                for j in range(1, n_nodes):
                    flux[j] = v_eff * conc[j - 1]  # upwind
                flux[0] = 0  # no flux from above (application handled separately)
                flux[n_nodes] = v_eff * conc[n_nodes - 1]  # bottom boundary

                # Dispersion
                D_eff = dispersion_length * v_pore / R
                for j in range(1, n_nodes):
                    disp_flux = D_eff * (conc[j - 1] - conc[j]) / dz
                    flux[j] += disp_flux

                # Update concentrations
                for j in range(n_nodes):
                    conc[j] += dt_sub * (flux[j] - flux[j + 1]) / dz

                # Leaching at bottom
                total_leached += flux[n_nodes] * theta * dz * dt_sub

        # Ensure non-negative and clamp underflow
        conc = np.maximum(conc, 0)
        conc[conc < 1e-30] = 0.0  # avoid subnormal float artefacts

        # ---- Record PEC ----
        # Topsoil PEC (mg/kg) = C_solution × R × theta / (bulk_density × 1000)
        pec_soil[day] = conc[0] * R * theta / (bulk_density * 1000) * 1e3  # mg/kg
        # Groundwater proxy: concentration at bottom node (µg/L ≈ µg/mL × 1000)
        pec_gw[day] = conc[-1] * 1000  # µg/L
        leachate[day] = conc[-1] * 1000  # µg/L

    # ── FOCUS metrics ───────────────────────────────────────────────
    annual_max = []
    for yr in range(years):
        start = yr * 365
        end = (yr + 1) * 365
        annual_max.append(float(np.max(pec_gw[start:end])))

    # 80th percentile (FOCUS standard: exclude first two years warm-up)
    if years > 2:
        pec_80th = float(np.percentile(annual_max[2:], 80))
    else:
        pec_80th = float(np.max(annual_max))

    # Mass balance
    total_remaining = float(np.sum(conc * R * dz * theta))
    mass_balance = {
        "applied_ug_m2": float(total_applied),
        "degraded_ug_m2": float(total_degraded),
        "leached_ug_m2": float(total_leached),
        "remaining_ug_m2": total_remaining,
    }

    return {
        "substance": substance["name"],
        "scenario": scenario["name"],
        "years": years,
        "degT50_used": float(deg_t50),
        "koc_used": float(koc),
        "is_quantum": quantum_params is not None,
        "time_days": list(range(n_days)),
        "pec_soil_mg_kg": pec_soil.tolist(),
        "pec_gw_ug_l": pec_gw.tolist(),
        "annual_max_pec_ug_l": annual_max,
        "pec_80th_ug_l": pec_80th,
        "total_leached_g_ha": float(total_leached / 1e6 * 1e4),  # µg/m² → g/ha
        "mass_balance": mass_balance,
    }


def run_comparison(substance, scenario, years=20, quantum_params=None):
    """
    Run both classical and quantum-enhanced simulations for comparison.

    Returns dict with 'classical' and 'quantum' result keys.
    """
    classical = run_simulation(substance, scenario, years, quantum_params=None)

    if quantum_params:
        quantum = run_simulation(substance, scenario, years, quantum_params=quantum_params)
    else:
        quantum = None

    # Downsample for JSON efficiency (monthly averages instead of daily)
    def downsample_monthly(daily_data, years):
        """Convert daily to monthly averages."""
        monthly = []
        for m in range(years * 12):
            start = m * 30
            end = min(start + 30, len(daily_data))
            if start < len(daily_data):
                monthly.append(float(np.mean(daily_data[start:end])))
        return monthly

    result = {
        "classical": {
            "pec_gw_monthly": downsample_monthly(classical["pec_gw_ug_l"], years),
            "pec_soil_monthly": downsample_monthly(classical["pec_soil_mg_kg"], years),
            "annual_max": classical["annual_max_pec_ug_l"],
            "pec_80th": classical["pec_80th_ug_l"],
            "total_leached": classical["total_leached_g_ha"],
            "degT50_used": classical["degT50_used"],
            "koc_used": classical["koc_used"],
        },
        "substance": substance["name"],
        "scenario": scenario["name"],
        "years": years,
        "months": list(range(years * 12)),
    }

    if quantum:
        result["quantum"] = {
            "pec_gw_monthly": downsample_monthly(quantum["pec_gw_ug_l"], years),
            "pec_soil_monthly": downsample_monthly(quantum["pec_soil_mg_kg"], years),
            "annual_max": quantum["annual_max_pec_ug_l"],
            "pec_80th": quantum["pec_80th_ug_l"],
            "total_leached": quantum["total_leached_g_ha"],
            "degT50_used": quantum["degT50_used"],
            "koc_used": quantum["koc_used"],
        }

    return result
