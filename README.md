# Existential Risk Analysis

A Python implementation of existential risk calculations based on economic growth models and mortality rates.

## Features
- Calculates existential risk cutoffs
- Analyzes scenarios with varying growth rates
- Considers mortality improvements
- Handles singularity scenarios
- Generates comparative tables of results

## Prerequisites
- Python 3.12+
- numpy
- math

## Installation
```bash
pip install numpy
```

## Usage
Run the analysis:
```bash
python existentialrisk.py
```

## Parameters
The model considers several key variables:
- Growth rates:
  - g_ai: AI-driven growth rate
  - g0: Baseline growth rate
- Mortality rates:
  - m_ai: AI-influenced mortality rate
  - m0: Baseline mortality rate
- Economic factors:
  - rho: Discount rate
  - rho_s: Social discount rate
  - v_c0: Value of life
  - gamma: Elasticity parameter

## Output
Generates Table 2: "Existential Risk Cutoffs: Mortality Improvements and Singularities"
- Compares fast growth (10%) vs singularity scenarios
- Analyzes different mortality rates (1% vs 0.5%)
- Considers multiple gamma values
- Shows cutoff values for each scenario combination

## Methodology
Based on economic models comparing welfare under:
- Baseline scenarios (without AI)
- AI-driven growth scenarios
- Various mortality improvement effects
- Different social welfare calculations


## Context (from 1_PLAN.md)
<!-- from 1_PLAN: papers/existential_risk/.context/1_PLAN.md -->

### 1. Goal

Existential Risk paper

### 2. Team

* **Lead**: [To be defined]

### 4. Key Dates & Timeline

| Date | Event | Type |
|------|-------|------|
| | [To be defined] | |

### 5. Logical Framework

[To be defined]

### 6. Methodology & Variables

[To be defined]

### 7. Anticipated Failure Points

* [To be defined]

### 8. Verification Strategy

* [To be defined]
