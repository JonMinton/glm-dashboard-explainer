#!/usr/bin/env python3
"""
Validate Tutorial 1: Gaussian GLM coefficients

This script verifies the coefficients shown in the Gaussian tutorial
match actual Python output using the UCI heart disease dataset.

Expected coefficients (from tutorial):
  Intercept: 203.37
  Age: -0.83
  ExerciseAngina: -14.25
  STDepression: -3.78
"""

import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

# Load heart disease data
with open("../../data/heart.json") as f:
    heart = pd.DataFrame(json.load(f))

# Convert ExerciseAngina to numeric if needed
if heart["ExerciseAngina"].dtype == object:
    heart["ExerciseAngina"] = (heart["ExerciseAngina"] == "Y").astype(int)

# Prepare data for GLM
X = heart[["Age", "ExerciseAngina", "Oldpeak"]]
X = sm.add_constant(X)  # Add intercept
y = heart["MaxHR"]

# Fit Gaussian GLM
model = sm.GLM(y, X, family=sm.families.Gaussian())
results = model.fit()

# Display results
print("=== Gaussian GLM Validation ===\n")
print("Model Summary:")
print(results.summary())

print("\n\nCoefficients:")
print(results.params)

# Compare to expected values
expected = {
    "const": 203.37,
    "Age": -0.83,
    "ExerciseAngina": -14.25,
    "Oldpeak": -3.78
}

actual = results.params.round(2)

print("\n\nValidation Check:")
print("Expected vs Actual:")
for name, exp_val in expected.items():
    act_val = actual.get(name, float('nan'))
    match = abs(exp_val - act_val) < 0.1
    status = "OK" if match else "MISMATCH"
    print(f"  {name}: expected {exp_val:.2f}, got {act_val:.2f} [{status}]")

if __name__ == "__main__":
    pass  # Script runs on import
