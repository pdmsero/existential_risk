import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Utility function
def utility(c, gamma, u_bar):
    if gamma == 1:
        return u_bar + math.log(c)
    else:
        return u_bar * c**(gamma-1) + 1 / (1 - gamma)

# Optimal time function
def optimal_time(g, delta, gamma, u_bar, c0):
    if gamma == 1:
        return max(0, (g/delta - (u_bar + math.log(c0))) / g)
    else:
        return max(0, math.log(max(1, g / (delta * utility(c0, gamma, u_bar)))) / (g * (gamma - 1)))

# Optimal consumption function
def optimal_consumption(g, delta, gamma, u_bar, c0):
    T = optimal_time(g, delta, gamma, u_bar, c0)
    return c0 * math.exp(g * T)

# Existential risk function
def existential_risk(delta, T):
    return max(0, min(1, 1 - math.exp(-delta * T)))

# Set initial parameters
c0 = 1  # Initial consumption normalized to 1

# Global variables
ValueStatisticalLife = 0
AverageLifeExpectancy = 0
ConsumptionPerCapita = 0

def set_country(country):
    global ValueStatisticalLife, AverageLifeExpectancy, ConsumptionPerCapita
    
    if country == "UK":
        # ValueStatisticalLife = 1800000 #VPF
        ValueStatisticalLife = 8590000 #J-value
        AverageLifeExpectancy = 41
        ConsumptionPerCapita = 25373
    elif country == "US":
        ValueStatisticalLife = 10000000
        AverageLifeExpectancy = 40
        ConsumptionPerCapita = 41666.6666666
    else:
        print(f"Data for {country} not available.")

# Usage
set_country("UK") 

# Function to calculate v(c_0)
def v_c0(VSL, ALE, Cpc):
    return (VSL / ALE) / Cpc

# v_c0 = 6  # Initial value of life
g = 0.10  # 10% growth rate

def calculate_u_bar(gamma):
    if abs(gamma - 1) < 1e-6:
        return v_c0(ValueStatisticalLife, AverageLifeExpectancy, ConsumptionPerCapita) - math.log(c0)
    else:
        return (v_c0(ValueStatisticalLife, AverageLifeExpectancy, ConsumptionPerCapita) - 1/(1-gamma)) / c0**(gamma-1)

# Main analysis for Table 1
table_1_results = []
for delta in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06]:
    for gamma in [1, 2, 3]:
        u_bar = calculate_u_bar(gamma)
        T_star = optimal_time(g, delta, gamma, u_bar, c0)
        c_star = optimal_consumption(g, delta, gamma, u_bar, c0)
        risk = existential_risk(delta, T_star)
        table_1_results.append((delta, gamma, c_star, T_star, risk))

def print_table_1(results):
    print("Table 1: Consumption and Existential Risk: Simple Model")
    print("\n")
    print("      δ = 1%             δ = 2%    ")
    print("γ    c*    T*  Exist.Risk    c*    T*  Exist.Risk")
    print("-" * 55)

    gammas = [1, 2, 3]
    deltas = [0.01, 0.02]

    for gamma in gammas:
        row = f"{gamma}   "
        for delta in deltas:
            result = next((r for r in results if r[0] == delta and r[1] == gamma), None)
            if result:
                _, _, c_star, T_star, risk = result
                row += f"{c_star:5.2f} {T_star:5.1f}   {risk:.2f}     "
            else:
                row += "  -     -      -     "
        print(row)

# After calculating table_1_results
print_table_1(table_1_results)

# Value of life function
def value_of_life(c, gamma, u_bar):
    if gamma == 1:
        return u_bar + np.log(c)
    else:
        return u_bar * c**(gamma-1) + 1 / (1 - gamma)

# Set up the consumption range
c = np.linspace(0.1, 2, 1000)

# Set parameters
u_bar = 0  # This value is chosen to make v(c) = 6 when c = 1 for gamma = 2
v_c0 = 6   # Value of life when c = 1

# Calculate u_bar for each gamma
def calculate_u_bar(gamma):
    if gamma == 1:
        return v_c0 - math.log(c0)
    else:
        return (v_c0 - 1/(1-gamma)) / c0**(gamma-1)

# Calculate and plot v(c) for each gamma
gammas = [1, 2, 3]
colors = ['b', 'g', 'r']

plt.figure(figsize=(10, 6))

for gamma, color in zip(gammas, colors):
    u_bar = calculate_u_bar(gamma)
    v = value_of_life(c, gamma, u_bar)
    plt.plot(c, v, color=color, label=f'γ = {gamma}')

plt.xlabel('Consumption, c')
plt.ylabel('Value of a Year of Life, v(c)')
plt.title('Value of Life vs Consumption for Different γ Values')
plt.legend()
plt.grid(True)

# Add a point and label for U.S. average today
plt.plot(1, 6, 'ko')
plt.annotate('U.S. average\ntoday', xy=(1, 6), xytext=(1.1, 4.5),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.ylim(0, 20)
plt.show()

# --- START OF TABLE 2 CALCULATIONS ---

# Social welfare function W(g, m)
def social_welfare(g, m, rho, rho_s, gamma, u_bar, v_c0):
    result = u_bar / ((rho + m) * (rho_s)) + c0**(1-gamma) / ((1-gamma)*(rho + m + (gamma - 1) * g) * (rho_s + (gamma - 1) * g))
    return result

# Existential risk cutoff function δ*
def existential_risk_cutoff(g_ai, m_ai, g0, m0, rho, rho_s,gamma, u_bar, v_c0):
    W_ai = social_welfare(g_ai, m_ai, rho, rho_s,gamma, u_bar, v_c0)
    W0 = social_welfare(g0, m0, rho, rho_s,gamma, u_bar, v_c0)
    if abs(W_ai - W0) < 1e-10:  # Use a small threshold for floating-point comparison
        return 0
    elif W_ai < W0:
        return float('nan')  # AI scenario worse than baseline
    else:
        return (W_ai - W0) / W_ai

# Parameters for calculations
g0 = 0.02  # Growth rate without AI
m0 = 0.01  # Mortality rate without AI
rho = 0.01  # Discount rate
rho_s= 0.01 # Social discount rate
v_c0 = 6  # Value of life

# Main function to calculate the table values
def calculate_table(rho_s=0.01, g_ai_values=None):
    if g_ai_values is None:
        g_ai_values = [0.10, 100]
    results = []
    for g_ai in g_ai_values:
        for m_ai in [0.01, 0.005]:
            for gamma in [1.00001, 2, 3]:
                u_bar = calculate_u_bar(gamma)
                delta_star = existential_risk_cutoff(g_ai, m_ai, g0, m0, rho, rho_s, gamma, u_bar, v_c0)
                results.append((g_ai, m_ai, gamma, delta_star))
    return results

def print_table(results):
    print("Table 2: Existential Risk Cutoffs: Mortality Improvements and Singularities")
    print("\n")
    print("                Fast growth: gai = 10%      Singularity: gai = ∞")
    print("                      — mai —                    — mai —")
    print("  γ              1%           0.5%           1%           0.5%")
    print("—" * 65)
    
    for gamma in [1.00001, 2, 3]:
        row = f"{gamma:<6}"
        for g_ai in [0.10, 100]:
            for m_ai in [0.01, 0.005]:
                delta_star = next(delta for ga, ma, gm, delta in results if ga == g_ai and ma == m_ai and gm == gamma)
                row += f"{delta_star:13.3f}" if not math.isnan(delta_star) else "      nan     "
        print(row)

# Run calculations and print the table
results = calculate_table()
print_table(results)

def print_table_3(results_baseline, results_near_zero):
    print("Table 3: Existential Risk Cutoffs with Near Zero Social Discounting")
    print("\n")
    print("                   Baseline         Near zero social")
    print("                  ρs = 1%             discounting")
    print("                                     ρs = 0.05%")
    print("                  — mai —             — mai —")
    print("  γ              1%        0.5%      1%        0.5%")
    print("—" * 65)
    
    gammas = [1.00001, 2, 3]
    m_ai_values = [0.01, 0.005]
    
    for gamma in gammas:
        row = f"{gamma:<6}"
        for results in [results_baseline, results_near_zero]:
            for m_ai in m_ai_values:
                delta_star = next((delta for ga, ma, gm, delta in results if ga == 0.10 and ma == m_ai and gm == gamma), float('nan'))
                row += f"{delta_star:10.3f}"
        print(row)

# Generate results for Table 3
results_baseline = calculate_table(rho_s=0.01, g_ai_values=[0.10])
results_near_zero = calculate_table(rho_s=0.0005, g_ai_values=[0.10])

# Print Table 3
print_table_3(results_baseline, results_near_zero)