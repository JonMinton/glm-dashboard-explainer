#!/usr/bin/env python3
"""
Validate Tutorial 4: Negative Binomial GLM coefficients

This script verifies the coefficients shown in the Negative Binomial tutorial
match actual Python output using the UCI Bike Sharing dataset.

Expected coefficients (from tutorial):
  Intercept: 8.1969
  temp: 1.7005
  hum: -0.4825
  windspeed: -1.1239
  workingday: 0.0519
  weathersit: -0.1421
  theta: 6.773
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Load the UCI Bike Sharing dataset (daily aggregates)
bike = pd.read_csv("../../data/day.csv")

print(f"Dataset dimensions: {bike.shape}")
print(f"\nCount summary:\n{bike['cnt'].describe()}")

# For Negative Binomial in statsmodels, alpha = 1/theta
# With theta = 6.773, alpha = 1/6.773 = 0.1476
expected_theta = 6.773
alpha = 1 / expected_theta

# Fit Negative Binomial model
model = smf.glm(
    'cnt ~ temp + hum + windspeed + workingday + weathersit',
    data=bike,
    family=sm.families.NegativeBinomial(alpha=alpha)
).fit()

# Display results
print("\n=== Negative Binomial GLM Validation ===\n")
print("Model Summary:")
print(model.summary())

print("\n\nCoefficients:")
print(model.params)

print(f"\n\nAlpha (1/theta) used: {alpha:.4f}")
print(f"Equivalent theta: {1/alpha:.3f}")

# Compare to expected values
expected = {
    "Intercept": 8.1969,
    "temp": 1.7005,
    "hum": -0.4825,
    "windspeed": -1.1239,
    "workingday": 0.0519,
    "weathersit": -0.1421
}

actual = model.params.round(4)

print("\n\nValidation Check:")
print("Expected vs Actual (Coefficients):")
for name, exp_val in expected.items():
    act_val = actual.get(name, float('nan'))
    match = abs(exp_val - act_val) < 0.01
    status = "OK" if match else "MISMATCH"
    print(f"  {name}: expected {exp_val:.4f}, got {act_val:.4f} [{status}]")

# Compare with Poisson for SE differences
print("\n\nComparison with Poisson (SE ratios):")
fit_pois = smf.glm(
    'cnt ~ temp + hum + windspeed + workingday + weathersit',
    data=bike,
    family=sm.families.Poisson()
).fit()

for name in expected.keys():
    se_pois = fit_pois.bse.get(name, float('nan'))
    se_nb = model.bse.get(name, float('nan'))
    ratio = se_nb / se_pois
    print(f"  {name}: Poisson SE={se_pois:.4f}, NegBin SE={se_nb:.4f}, Ratio={ratio:.1f}x")

# Model fit statistics
print("\n\nModel Fit Statistics:")
print(f"  Deviance: {model.deviance:.2f}")
print(f"  Deviance/df: {model.deviance / model.df_resid:.2f} (should be ~1 for good fit)")
print(f"  AIC (NegBin): {model.aic:.2f}")
print(f"  AIC (Poisson): {fit_pois.aic:.2f}")

if __name__ == "__main__":
    pass  # Script runs on import
