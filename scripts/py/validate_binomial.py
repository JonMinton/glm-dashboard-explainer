#!/usr/bin/env python3
"""
Validate Tutorial 2: Binomial GLM (Logistic Regression) coefficients

This script verifies the coefficients shown in the Binomial tutorial
match actual Python output using the UCI heart disease dataset.

Expected coefficients (from tutorial):
  Intercept: -3.1655
  age: 0.0359
  sex: 1.6745
  cp: 0.8963
  thalach: -0.0247
  oldpeak: 0.6829
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Load the UCI Heart Disease dataset
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
cols = ["age", "sex", "cp", "trestbps", "chol", "fbs",
        "restecg", "thalach", "exang", "oldpeak",
        "slope", "ca", "thal", "target"]
heart = pd.read_csv(url, header=None, names=cols)

# Binarise target: 0 = no disease, 1 = disease
heart['target'] = (heart['target'] > 0).astype(int)

# Fit logistic regression
model = smf.glm(
    formula="target ~ age + sex + cp + thalach + oldpeak",
    data=heart,
    family=sm.families.Binomial()
).fit()

# Display results
print("=== Binomial GLM (Logistic Regression) Validation ===\n")
print("Model Summary:")
print(model.summary())

print("\n\nCoefficients:")
print(model.params)

# Compare to expected values
expected = {
    "Intercept": -3.1655,
    "age": 0.0359,
    "sex": 1.6745,
    "cp": 0.8963,
    "thalach": -0.0247,
    "oldpeak": 0.6829
}

actual = model.params.round(4)

print("\n\nValidation Check:")
print("Expected vs Actual:")
for name, exp_val in expected.items():
    act_val = actual.get(name, float('nan'))
    match = abs(exp_val - act_val) < 0.01
    status = "OK" if match else "MISMATCH"
    print(f"  {name}: expected {exp_val:.4f}, got {act_val:.4f} [{status}]")

# Additional model stats
print("\n\nModel Fit Statistics:")
print(f"  Null deviance: {model.null_deviance:.2f}")
print(f"  Residual deviance: {model.deviance:.2f}")
print(f"  AIC: {model.aic:.2f}")

if __name__ == "__main__":
    pass  # Script runs on import
