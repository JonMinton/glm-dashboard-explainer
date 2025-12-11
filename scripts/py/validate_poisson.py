#!/usr/bin/env python3
"""
Validate Tutorial 3: Poisson GLM coefficients

This script verifies the coefficients shown in the Poisson tutorial
match actual Python output using the UCI Bike Sharing dataset.

Expected coefficients (from tutorial):
  Intercept: 8.2391
  temp: 1.3971
  hum: -0.3568
  windspeed: -0.9673
  workingday: 0.0389
  weathersit: -0.1298
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Load the UCI Bike Sharing dataset (daily aggregates)
# Note: Dataset needs to be downloaded from UCI or Kaggle
bike = pd.read_csv("../../data/day.csv")

print(f"Dataset dimensions: {bike.shape}")
print(f"\nCount summary:\n{bike['cnt'].describe()}")

# Fit Poisson regression with log link
model = smf.glm(
    'cnt ~ temp + hum + windspeed + workingday + weathersit',
    data=bike,
    family=sm.families.Poisson()
).fit()

# Display results
print("\n=== Poisson GLM Validation ===\n")
print("Model Summary:")
print(model.summary())

print("\n\nCoefficients:")
print(model.params)

# Compare to expected values
expected = {
    "Intercept": 8.2391,
    "temp": 1.3971,
    "hum": -0.3568,
    "windspeed": -0.9673,
    "workingday": 0.0389,
    "weathersit": -0.1298
}

actual = model.params.round(4)

print("\n\nValidation Check:")
print("Expected vs Actual:")
for name, exp_val in expected.items():
    act_val = actual.get(name, float('nan'))
    match = abs(exp_val - act_val) < 0.01
    status = "OK" if match else "MISMATCH"
    print(f"  {name}: expected {exp_val:.4f}, got {act_val:.4f} [{status}]")

# Check for overdispersion
print("\n\nOverdispersion Check:")
dispersion_ratio = model.deviance / model.df_resid
print(f"  Residual deviance: {model.deviance:.2f}")
print(f"  Degrees of freedom: {model.df_resid}")
print(f"  Dispersion ratio: {dispersion_ratio:.2f} (should be ~1 for Poisson)")

if dispersion_ratio > 2:
    print("  WARNING: Severe overdispersion detected! Consider Negative Binomial.")

# Additional model stats
print("\n\nModel Fit Statistics:")
print(f"  Null deviance: {model.null_deviance:.2f}")
print(f"  Residual deviance: {model.deviance:.2f}")
print(f"  AIC: {model.aic:.2f}")

if __name__ == "__main__":
    pass  # Script runs on import
