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
# Value of a statistical life-year (the MARGINAL VSL object), in consumption
# units: VSLY(c) = v(c) / v'(c). This is the Hall-Jones (2007) / Becker-
# Philipson-Soares value-of-a-life-year: the period flow value of being alive
# divided by the marginal utility of consumption (which converts utils to
# consumption units). VSL = VSLY x remaining life expectancy.
#   v(c) = c^(1-gamma)/(1-gamma) + u_bar,  v'(c) = c^(-gamma)
#   => VSLY(c) = c/(1-gamma) + u_bar c^gamma   (gamma != 1)
#   => VSLY(c) = c (log c + u_bar)             (gamma = 1)
# ======================================================================

def value_of_life_year(c, gamma, u_bar):
    if abs(gamma - 1) < 1e-9:
        return c * (math.log(c) + u_bar)
    return c / (1 - gamma) + u_bar * c ** gamma


# ======================================================================
# u_bar calibration from the VSL anchor v_c0, derived from the MARGINAL object.
# v_c0 is the empirical value-of-a-life-year per unit consumption,
#   v_c0 = VSL / (LifeExpectancy * Consumption per capita) = VSLY(c0)/c0.
# Setting VSLY(c0)/c0 = v_c0 at the normalisation c0 = 1 (so v'(c0)=1) gives
#   u_bar = v_c0 - 1/(1-gamma)   (gamma != 1),   u_bar = v_c0   (gamma = 1).
# The c0=1 normalisation makes v'(c0)=1, so the marginal calibration coincides
# numerically with level-matching v(c0)=v_c0; the object remains marginal.
# ======================================================================

def calibrate_u_bar(v_c0, gamma, c0=1.0):
    if abs(gamma - 1) < 1e-9:
        return v_c0 / c0 - math.log(c0)
    # u_bar from VSLY(c0)/c0 = v_c0  =>  u_bar = (v_c0 - 1/((1-gamma))) c0^(-gamma) ... at c0=1:
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
        # Log case: must match social_welfare's gamma->1 limit EXACTLY, which carries
        # the cross-cohort growth term g/(D3 D4^2) in addition to g/(D3^2 D4).
        # Dropping it (earlier bug) understated the consumption channel and inflated
        # the flow-utility share in every gamma=1 row of Table 1.
        cons_ai = (math.log(c0) / (D3_ai * D4)
                   + g_ai / (D3_ai ** 2 * D4)
                   + g_ai / (D3_ai * D4 ** 2))
        cons_0 = (math.log(c0) / (D3_0 * D4)
                  + g0 / (D3_0 ** 2 * D4)
                  + g0 / (D3_0 * D4 ** 2))
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
# Growth -> mortality spillover extension
# ----------------------------------------------------------------------
# The baseline decomposition routes ALL of growth's welfare value through
# consumption and NONE through mortality, even though growth historically
# REDUCES mortality (Preston 1975; Cutler-Deaton-Lleras-Muney 2006; the
# Hall-Jones value-of-life lineage). We therefore attribute a fraction f of
# the observed mortality improvement (m0 - m_ai) to growth, and re-decompose
# the welfare gain into:
#   - a GROWTH-inclusive channel: direct consumption gain + the flow-utility
#     gain from the growth-attributable part of the mortality improvement;
#   - a residual AUTONOMOUS-mortality channel.
# The flow-utility gain is split exactly by telescoping through an intermediate
# mortality m_mid = m0 - (1-f)(m0 - m_ai) (autonomous improvement only):
#   flow_auto   = u_bar [1/((rho+m_mid) D4) - 1/((rho+m0) D4)]
#   flow_growth = total_flow_gain - flow_auto.
# f is the empirically contested object; we sweep it rather than assert a value.
# ======================================================================

def welfare_decomposition_spillover(g_ai, m_ai, g0, m0, rho, rho_s, gamma, u_bar,
                                    f, c0=1.0):
    """Re-decompose the welfare gain attributing a fraction f of the mortality
    improvement to growth. Returns the growth-inclusive channel share."""
    base = welfare_decomposition(g_ai, m_ai, g0, m0, rho, rho_s, gamma, u_bar, c0)
    cons_gain = base["consumption_channel"]
    flow_gain = base["flow_utility_channel"]
    total = base["total"]
    D4 = rho_s
    m_mid = m0 - (1.0 - f) * (m0 - m_ai)            # autonomous improvement only
    flow_auto = u_bar * (1.0 / ((rho + m_mid) * D4) - 1.0 / ((rho + m0) * D4))
    flow_growth = flow_gain - flow_auto
    growth_inclusive = cons_gain + flow_growth
    return {
        "f": f,
        "growth_inclusive_channel": growth_inclusive,
        "autonomous_mortality_channel": flow_auto,
        "growth_inclusive_share": growth_inclusive / total if total != 0 else float('nan'),
    }


def growth_majority_threshold(g_ai, m_ai, g0, m0, rho, rho_s, gamma, u_bar, c0=1.0):
    """Smallest spillover fraction f* at which the growth-inclusive channel
    reaches a 50% share of the welfare gain. Returns NaN if never within [0,1]."""
    lo, hi = 0.0, 1.0
    s = lambda f: welfare_decomposition_spillover(
        g_ai, m_ai, g0, m0, rho, rho_s, gamma, u_bar, f, c0)["growth_inclusive_share"]
    if s(hi) < 0.5:
        return float('nan')
    if s(lo) >= 0.5:
        return 0.0
    for _ in range(100):                            # bisection
        mid = 0.5 * (lo + hi)
        if s(mid) >= 0.5:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def table_growth_spillover(f_list=None, g_ai=0.10, m_ai=0.005, g0=0.02, m0=0.01,
                           rho=0.01, rho_s=0.01, gamma=2.0, v_c0=6.0, c0=1.0):
    """Growth-inclusive share at the headline scenario as f varies."""
    if f_list is None:
        f_list = [0.0, 0.25, 0.5, 0.75, 1.0]
    u_bar = calibrate_u_bar(v_c0, gamma, c0)
    rows = []
    for f in f_list:
        d = welfare_decomposition_spillover(g_ai, m_ai, g0, m0, rho, rho_s,
                                            gamma, u_bar, f, c0)
        rows.append({"f": f,
                     "growth_inclusive_share": d["growth_inclusive_share"],
                     "mortality_share": 1.0 - d["growth_inclusive_share"]})
    return pd.DataFrame(rows)


# ======================================================================
# Internal-consistency and well-posedness guards (regression tests)
# ======================================================================

def check_decomposition_consistency(rho=0.01, rho_s=0.01, g0=0.02, m0=0.01,
                                    v_c0=6.0, c0=1.0, tol=1e-6):
    """The two channels must sum to W_AI(0) - W_0 from social_welfare, in every
    cell and every gamma. Guards against the gamma=1 cross-cohort-term bug."""
    bad = []
    for g_ai in [0.05, 0.10, 0.20]:
        for m_ai in [0.01, 0.005]:
            for gamma in [1.0, 2.0, 3.0]:
                u_bar = calibrate_u_bar(v_c0, gamma, c0)
                d = welfare_decomposition(g_ai, m_ai, g0, m0, rho, rho_s, gamma, u_bar, c0)
                W = (social_welfare(g_ai, m_ai, 0.0, rho, rho_s, gamma, u_bar, c0)
                     - social_welfare(g0, m0, 0.0, rho, rho_s, gamma, u_bar, c0))
                if abs(d["total"] - W) > tol * max(1.0, abs(W)):
                    bad.append((g_ai, m_ai, gamma, d["total"], W))
    return bad


def check_cutoff_monotonicity(rho=0.01, rho_s=0.01, g0=0.02, m0=0.01,
                              v_c0=6.0, c0=1.0, n=2001, delta_max=1.0):
    """W_AI(delta) must be strictly decreasing for delta* to be unique (Def 1)."""
    import numpy as np
    bad = []
    for g_ai in [0.05, 0.10, 0.20]:
        for m_ai in [0.01, 0.005]:
            for gamma in [1.0, 2.0, 3.0]:
                u_bar = calibrate_u_bar(v_c0, gamma, c0)
                ds = np.linspace(0, delta_max, n)
                W = np.array([social_welfare(g_ai, m_ai, d, rho, rho_s, gamma, u_bar, c0)
                              for d in ds])
                if not np.all(np.diff(W) <= 1e-12):
                    bad.append((g_ai, m_ai, gamma))
    return bad


# ======================================================================
# Figure: the rho_s -> 0 channel reversal between log and CRRA
# ======================================================================

def make_figures(outdir="paper/figures"):
    import os
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(outdir, exist_ok=True)

    rho, g0, m0, v_c0 = 0.01, 0.02, 0.01, 6.0
    g_ai, m_ai = 0.10, 0.005
    rho_s_grid = np.geomspace(2e-4, 0.05, 60)

    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    # Panel A: flow-channel share vs rho_s, gamma=1 vs gamma=2 (the reversal).
    for gamma, style in [(1.0, "--"), (2.0, "-")]:
        ub = calibrate_u_bar(v_c0, gamma)
        share = [welfare_decomposition(g_ai, m_ai, g0, m0, rho, rs, gamma, ub)["flow_share"]
                 for rs in rho_s_grid]
        ax[0].semilogx(rho_s_grid, share, style, label=fr"$\gamma={int(gamma)}$")
    ax[0].axhline(0.5, color="0.6", lw=0.8, ls=":")
    ax[0].set_xlabel(r"social discount rate $\rho_s$")
    ax[0].set_ylabel("flow (mortality) channel share")
    ax[0].set_title(r"(a) channel share: the $\rho_s\to0$ reversal")
    ax[0].legend(frameon=False)
    ax[0].set_ylim(-0.02, 1.02)

    # Panel B: growth-inclusive share vs spillover fraction f (gamma=2).
    ub2 = calibrate_u_bar(v_c0, 2.0)
    f_grid = np.linspace(0, 1, 101)
    gi = [welfare_decomposition_spillover(g_ai, m_ai, g0, m0, rho, 0.01, 2.0, ub2, f)["growth_inclusive_share"]
          for f in f_grid]
    fstar = growth_majority_threshold(g_ai, m_ai, g0, m0, rho, 0.01, 2.0, ub2)
    ax[1].plot(f_grid, gi, "-")
    ax[1].axhline(0.5, color="0.6", lw=0.8, ls=":")
    ax[1].axvline(fstar, color="C3", lw=0.8, ls="--", label=fr"$f^*={fstar:.2f}$")
    ax[1].set_xlabel("fraction $f$ of mortality gain attributable to growth")
    ax[1].set_ylabel("growth-inclusive channel share")
    ax[1].set_title(r"(b) headline inverts at $f^*$ ($\gamma=2$)")
    ax[1].legend(frameon=False)
    ax[1].set_ylim(-0.02, 1.02)

    fig.tight_layout()
    path = os.path.join(outdir, "channel_shares.pdf")
    fig.savefig(path)
    plt.close(fig)
    return path


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

    print()
    print("=" * 70)
    print("Extension: growth -> mortality spillover (how far does 94% move?)")
    print("=" * 70)
    ub2 = calibrate_u_bar(6.0, 2.0)
    df_sp = table_growth_spillover()
    print(df_sp.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    fstar = growth_majority_threshold(0.10, 0.005, 0.02, 0.01, 0.01, 0.01, 2.0, ub2)
    print(f"\n  Growth becomes the majority channel once f* = {fstar:.3f} of the")
    print(f"  mortality improvement is attributable to growth.")

    print()
    print("=" * 70)
    print("Regression / well-posedness checks")
    print("=" * 70)
    bad_dec = check_decomposition_consistency()
    bad_mono = check_cutoff_monotonicity()
    assert not bad_dec, f"decomposition inconsistency: {bad_dec}"
    assert not bad_mono, f"W_AI(delta) not monotone: {bad_mono}"
    print("  [OK] decomposition channels sum to W_AI(0)-W_0 in all cells/gamma")
    print("  [OK] W_AI(delta) strictly decreasing on [0,1] in all cells/gamma (delta* unique)")

    fig_path = make_figures()
    print(f"  [OK] figure written: {fig_path}")
    print("=" * 70)
