"""
existentialrisk.py - Existential-risk cutoff computation.

Models a representative-agent CRRA economy with mortality rate m, growth rate g,
and an extinction hazard delta. Computes the cutoff delta* at which a
high-growth, low-mortality scenario delivers the same social welfare as a
baseline.

Welfare functional (closed form under CRRA + constant growth):

  W(g, m; rho, rho_s, gamma, u_bar) =
      c_0^(1-gamma) / [ (1-gamma) * D_1(g,m) * D_2(g) ]
    + u_bar / [ D_3(m) * D_4 ]

where
  D_1(g, m) = (rho + m) + (gamma - 1) g
  D_2(g)    = rho_s + (gamma - 1) g
  D_3(m)    = rho + m
  D_4       = rho_s

With extinction hazard delta added to the high-growth scenario:
  W_AI(delta) substitutes (m_AI + delta) for m_AI in D_1, D_3
  and (rho_s + delta) for rho_s in D_2, D_4.

The cutoff delta* solves W_AI(delta*) = W_0 by numerical root-finding.

NOTE: this replaces an earlier version in which (a) the utility function
in line 7 used a non-standard form u(c) = u_bar c^(gamma-1) + 1/(1-gamma),
inconsistent with the standard CRRA u(c) = c^(1-gamma)/(1-gamma) + u_bar
used in social_welfare; and (b) the function existential_risk_cutoff
returned (W_AI - W_0)/W_AI, not the actual cutoff hazard. Both are fixed.
"""

import math
import numpy as np
from scipy.optimize import brentq
import pandas as pd


# ======================================================================
# Standard CRRA utility (consistent throughout)
# u(c) = c^(1-gamma)/(1-gamma) + u_bar  for gamma != 1
# u(c) = log(c) + u_bar                  for gamma = 1
# ======================================================================

def utility(c, gamma, u_bar):
    if abs(gamma - 1) < 1e-9:
        return math.log(c) + u_bar
    return c ** (1 - gamma) / (1 - gamma) + u_bar


# ======================================================================
# u_bar calibration from VSL anchor v_c0
# v(c_0) = v_c0  with c_0 = 1  =>  u_bar = v_c0 - 1/(1-gamma)  (gamma != 1)
#                                  u_bar = v_c0                (gamma = 1)
# ======================================================================

def calibrate_u_bar(v_c0, gamma, c0=1.0):
    if abs(gamma - 1) < 1e-9:
        return v_c0 - math.log(c0)
    return v_c0 - c0 ** (1 - gamma) / (1 - gamma)


# ======================================================================
# Social welfare (closed form under CRRA + constant growth + Poisson hazard)
# ======================================================================

def social_welfare(g, m, delta, rho, rho_s, gamma, u_bar, c0=1.0):
    """
    Social welfare W under growth g, mortality m, extinction hazard delta.
    The hazard delta enters as an additional discount-rate increment to both
    the private-mortality channel (m + delta) and the social-discount channel
    (rho_s + delta).
    """
    m_eff = m + delta
    rho_s_eff = rho_s + delta

    D1 = (rho + m_eff) + (gamma - 1) * g
    D2 = rho_s_eff + (gamma - 1) * g
    D3 = rho + m_eff
    D4 = rho_s_eff

    if abs(gamma - 1) < 1e-9:
        # Logarithmic case: handle separately via l'Hospital
        # W = (log c0)/D4_int + g/(D4_int)^2 + u_bar/(D3 D4)
        # where D4_int = D3 + D2 - rho... actually just integrate directly.
        # For gamma -> 1: c^(1-gamma)/(1-gamma) -> log(c).
        # integral of e^(-D3 t) log(c0 e^(gt)) dt = log(c0)/D3 + g/D3^2
        # then integrate over generations: W = log(c0)/(D3 D4) + g/(D3^2 D4) (approx)
        # Use the limit form
        cons_term = math.log(c0) / (D3 * D4) + g / (D3 ** 2 * D4) + g / (D3 * D4 ** 2)
    else:
        cons_term = c0 ** (1 - gamma) / ((1 - gamma) * D1 * D2)

    flow_term = u_bar / (D3 * D4)

    return cons_term + flow_term


# ======================================================================
# Existential-risk cutoff: find delta* such that W_AI(delta*) = W_0
# ======================================================================

def existential_risk_cutoff(g_ai, m_ai, g0, m0, rho, rho_s, gamma, u_bar, c0=1.0,
                             delta_max=1.0):
    """
    Find delta* > 0 such that social_welfare(g_ai, m_ai, delta*) = social_welfare(g0, m0, 0).
    Returns 0 if W_AI(0) <= W_0 (AI scenario weakly worse even at zero hazard).
    Returns NaN if no root in [0, delta_max].
    """
    W_0 = social_welfare(g0, m0, 0.0, rho, rho_s, gamma, u_bar, c0)
    W_AI_0 = social_welfare(g_ai, m_ai, 0.0, rho, rho_s, gamma, u_bar, c0)

    if W_AI_0 <= W_0:
        return 0.0

    def f(delta):
        return social_welfare(g_ai, m_ai, delta, rho, rho_s, gamma, u_bar, c0) - W_0

    # f(0) > 0 by construction; f(delta_max) should be negative for delta_max large.
    if f(delta_max) > 0:
        return float('nan')  # AI dominates even at very high hazard; cutoff > delta_max
    try:
        return brentq(f, 0.0, delta_max, xtol=1e-10)
    except ValueError:
        return float('nan')


# ======================================================================
# Welfare-gain decomposition: separate the consumption channel from the
# u_bar (life-value) channel. Shows which channel drives the cutoff.
# ======================================================================

def welfare_decomposition(g_ai, m_ai, g0, m0, rho, rho_s, gamma, u_bar, c0=1.0):
    """
    Decompose W_AI(0) - W_0 into:
      - consumption channel: c_0^(1-gamma)/(1-gamma) * [1/(D1_ai D2_ai) - 1/(D1_0 D2_0)]
      - u_bar channel:        u_bar * [1/(D3_ai D4_0) - 1/(D3_0 D4_0)]    (delta=0 case)
    where D's are evaluated at the respective scenario.
    """
    D1_ai = (rho + m_ai) + (gamma - 1) * g_ai
    D2_ai = rho_s + (gamma - 1) * g_ai
    D3_ai = rho + m_ai
    D4 = rho_s

    D1_0 = (rho + m0) + (gamma - 1) * g0
    D2_0 = rho_s + (gamma - 1) * g0
    D3_0 = rho + m0

    if abs(gamma - 1) < 1e-9:
        cons_ai = math.log(c0) / (D3_ai * D4) + g_ai / (D3_ai ** 2 * D4)
        cons_0 = math.log(c0) / (D3_0 * D4) + g0 / (D3_0 ** 2 * D4)
    else:
        cons_ai = c0 ** (1 - gamma) / ((1 - gamma) * D1_ai * D2_ai)
        cons_0 = c0 ** (1 - gamma) / ((1 - gamma) * D1_0 * D2_0)

    cons_gain = cons_ai - cons_0
    flow_gain = u_bar * (1.0 / (D3_ai * D4) - 1.0 / (D3_0 * D4))

    return {
        "consumption_channel": cons_gain,
        "flow_utility_channel": flow_gain,
        "total": cons_gain + flow_gain,
        "flow_share": flow_gain / (cons_gain + flow_gain) if (cons_gain + flow_gain) != 0 else float('nan'),
    }


# ======================================================================
# VSL anchor
# ======================================================================

def v_c0_from_country(country):
    """Returns v_c0 = (VSL / Life Expectancy) / Consumption per capita."""
    data = {
        "UK": {"VSL": 8590000, "ALE": 41, "Cpc": 25373},
        "US": {"VSL": 10000000, "ALE": 40, "Cpc": 41666.67},
    }
    if country not in data:
        raise ValueError(f"No data for {country}")
    d = data[country]
    return (d["VSL"] / d["ALE"]) / d["Cpc"]


# ======================================================================
# Headline tables
# ======================================================================

def table_existential_cutoffs(rho=0.01, rho_s=0.01, g0=0.02, m0=0.01,
                                v_c0=6.0, c0=1.0, g_ai_list=None,
                                m_ai_list=None, gamma_list=None):
    """Compute delta* across a parameter grid. Returns DataFrame."""
    if g_ai_list is None:
        g_ai_list = [0.05, 0.10, 0.20]
    if m_ai_list is None:
        m_ai_list = [0.01, 0.005]
    if gamma_list is None:
        gamma_list = [1.0, 2.0, 3.0]

    rows = []
    for g_ai in g_ai_list:
        for m_ai in m_ai_list:
            for gamma in gamma_list:
                u_bar = calibrate_u_bar(v_c0, gamma, c0)
                delta_star = existential_risk_cutoff(g_ai, m_ai, g0, m0, rho, rho_s,
                                                       gamma, u_bar, c0)
                decomp = welfare_decomposition(g_ai, m_ai, g0, m0, rho, rho_s,
                                                 gamma, u_bar, c0)
                rows.append({
                    "g_ai": g_ai,
                    "m_ai": m_ai,
                    "gamma": gamma,
                    "u_bar": u_bar,
                    "delta_star": delta_star,
                    "flow_share": decomp["flow_share"],
                    "cons_channel": decomp["consumption_channel"],
                    "flow_channel": decomp["flow_utility_channel"],
                })
    return pd.DataFrame(rows)


def table_discount_sensitivity(rho_s_list=None, **kw):
    """Sensitivity of delta* to social discount rate rho_s."""
    if rho_s_list is None:
        rho_s_list = [0.0005, 0.001, 0.005, 0.01, 0.03]
    rows = []
    for rho_s in rho_s_list:
        df = table_existential_cutoffs(rho_s=rho_s, **kw)
        # Pick the headline case: g_ai=0.10, m_ai=0.005, gamma=2
        sub = df[(df["g_ai"] == 0.10) & (df["m_ai"] == 0.005) & (df["gamma"] == 2.0)]
        if len(sub) > 0:
            r = sub.iloc[0]
            rows.append({
                "rho_s": rho_s,
                "delta_star": r["delta_star"],
                "flow_share": r["flow_share"],
            })
    return pd.DataFrame(rows)


def table_vsl_sensitivity(v_c0_list=None, **kw):
    """Sensitivity of delta* to VSL anchor v_c0 (drives u_bar)."""
    if v_c0_list is None:
        v_c0_list = [2.0, 4.0, 6.0, 8.0, 10.0]
    rows = []
    for v_c0 in v_c0_list:
        df = table_existential_cutoffs(v_c0=v_c0, **kw)
        sub = df[(df["g_ai"] == 0.10) & (df["m_ai"] == 0.005) & (df["gamma"] == 2.0)]
        if len(sub) > 0:
            r = sub.iloc[0]
            rows.append({
                "v_c0": v_c0,
                "u_bar": r["u_bar"],
                "delta_star": r["delta_star"],
                "flow_share": r["flow_share"],
            })
    return pd.DataFrame(rows)


# ======================================================================
# Main: run the tables
# ======================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("VSL anchors")
    print("=" * 70)
    for country in ["UK", "US"]:
        v = v_c0_from_country(country)
        print(f"  {country}: v_c0 = {v:.2f}")

    print()
    print("=" * 70)
    print("Table 1: Existential-risk cutoffs across scenarios (v_c0 = 6, rho_s = 1%)")
    print("=" * 70)
    df1 = table_existential_cutoffs()
    print(df1.to_string(index=False, float_format=lambda x: f"{x:.5f}"))

    print()
    print("=" * 70)
    print("Table 2: Sensitivity to social discount rate (g_ai=10%, m_ai=0.5%, gamma=2)")
    print("=" * 70)
    df2 = table_discount_sensitivity()
    print(df2.to_string(index=False, float_format=lambda x: f"{x:.5f}"))

    print()
    print("=" * 70)
    print("Table 3: Sensitivity to VSL anchor v_c0 (g_ai=10%, m_ai=0.5%, gamma=2, rho_s=1%)")
    print("=" * 70)
    df3 = table_vsl_sensitivity()
    print(df3.to_string(index=False, float_format=lambda x: f"{x:.5f}"))

    print()
    print("=" * 70)
    print("Headline decomposition: which channel drives the cutoff?")
    print("=" * 70)
    decomp = welfare_decomposition(0.10, 0.005, 0.02, 0.01, 0.01, 0.01, 2.0,
                                     calibrate_u_bar(6.0, 2.0))
    print(f"  Consumption channel:  {decomp['consumption_channel']:.4f}")
    print(f"  Flow-utility channel: {decomp['flow_utility_channel']:.4f}")
    print(f"  Flow-channel share:   {decomp['flow_share']*100:.1f}%")
    print()
    print("  At the headline calibration, the flow-utility (u_bar / VSL) channel")
    print("  is the dominant driver. Growth contributes a small share.")
    print("=" * 70)
