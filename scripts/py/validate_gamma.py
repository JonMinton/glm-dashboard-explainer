#!/usr/bin/env python3
"""
Validate Tutorial 5: Gamma GLM coefficients

This script verifies the coefficients shown in the Gamma tutorial
match actual Python output using the UCI heart disease dataset.

Expected coefficients (from tutorial):
  Intercept: 4.6460
  age: 0.0040
  exang: 0.0012
  oldpeak: 0.0155
  Shape parameter: ~61.75
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Load UCI Heart Disease data
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
cols = ["age", "sex", "cp", "trestbps", "chol", "fbs",
        "restecg", "thalach", "exang", "oldpeak",
        "slope", "ca", "thal", "target"]
heart = pd.read_csv(url, header=None, names=cols, na_values="?")
heart = heart.dropna()

print(f"Dataset dimensions: {heart.shape}")
print(f"\nBlood pressure (trestbps) summary:\n{heart['trestbps'].describe()}")

# Fit Gamma GLM with log link
model = smf.glm(
    'trestbps ~ age + exang + oldpeak',
    data=heart,
    family=sm.families.Gamma(link=sm.families.links.Log())
).fit()

# Display results
print("\n=== Gamma GLM Validation ===\n")
print("Model Summary:")
print(model.summary())

print("\n\nCoefficients:")
print(model.params)

# Shape parameter (1/scale in statsmodels)
print(f"\n\nScale (dispersion): {model.scale:.6f}")
shape = 1 / model.scale
print(f"Shape parameter (1/scale): {shape:.2f}")

# Compare to expected values
expected = {
    "Intercept": 4.6460,
    "age": 0.0040,
    "exang": 0.0012,
    "oldpeak": 0.0155
}

actual = model.params.round(4)

print("\n\nValidation Check:")
print("Expected vs Actual (Coefficients):")
for name, exp_val in expected.items():
    act_val = actual.get(name, float('nan'))
    match = abs(exp_val - act_val) < 0.001
    status = "OK" if match else "MISMATCH"
    print(f"  {name}: expected {exp_val:.4f}, got {act_val:.4f} [{status}]")

# Check shape parameter
expected_shape = 61.75
match_shape = abs(expected_shape - shape) < 1
status_shape = "OK" if match_shape else "MISMATCH"
print(f"  shape: expected {expected_shape:.2f}, got {shape:.2f} [{status_shape}]")

# Compare with Gaussian
print("\n\nComparison with Gaussian:")
fit_gauss = smf.glm(
    'trestbps ~ age + exang + oldpeak',
    data=heart,
    family=sm.families.Gaussian()
).fit()

print(f"  Gamma AIC: {model.aic:.1f}")
print(f"  Gaussian AIC: {fit_gauss.aic:.1f}")
print(f"  Difference: {fit_gauss.aic - model.aic:.1f} (lower is better)")

# Model fit statistics
print("\n\nModel Fit Statistics:")
print(f"  Deviance: {model.deviance:.4f}")
print(f"  Null deviance: {model.null_deviance:.4f}")

if __name__ == "__main__":
    pass  # Script runs on import
