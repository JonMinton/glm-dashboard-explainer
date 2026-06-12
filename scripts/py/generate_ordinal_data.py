"""
Generate synthetic pain levels dataset for Tutorial 07: Ordinal Regression.

Uses a proportional odds (cumulative logit) model as the data-generating process.

True model parameters:
  Thresholds: alpha_1 = -2.0, alpha_2 = 0.5, alpha_3 = 2.5
  Coefficients: beta_treatmentB = -0.8, beta_placebo = 0.6,
                beta_dose = -0.02, beta_age = 0.03

P(Y <= j) = logistic(alpha_j - X*beta)  (polr convention: minus sign)
"""

import numpy as np
import json
import os

np.random.seed(42)

n = 350

# --- Generate predictors ---

# Treatment: A (40%), B (40%), Placebo (20%)
treatment_probs = [0.40, 0.40, 0.20]
treatment_labels = ["A", "B", "Placebo"]
treatment = np.random.choice(treatment_labels, size=n, p=treatment_probs)

# Dose: uniform(10, 100) for A/B, 0 for Placebo
dose_mg = np.zeros(n, dtype=int)
for i in range(n):
    if treatment[i] in ("A", "B"):
        dose_mg[i] = int(round(np.random.uniform(10, 100)))
    else:
        dose_mg[i] = 0

# Age: uniform(25, 75)
age = np.array([int(round(np.random.uniform(25, 75))) for _ in range(n)])

# --- True model parameters ---
alpha = np.array([-2.0, 0.5, 2.5])  # Thresholds (J-1 = 3 for 4 categories)
beta_treatmentB = -0.8
beta_placebo = 0.6
beta_dose = -0.02
beta_age = 0.03

# --- Compute linear predictor (X*beta, no thresholds) ---
xb = np.zeros(n)
for i in range(n):
    if treatment[i] == "B":
        xb[i] += beta_treatmentB
    elif treatment[i] == "Placebo":
        xb[i] += beta_placebo
    xb[i] += beta_dose * dose_mg[i]
    xb[i] += beta_age * age[i]

# --- Compute cumulative probabilities (polr convention: alpha_j - xb) ---
def logistic(x):
    return 1.0 / (1.0 + np.exp(-x))

# P(Y <= j) = logistic(alpha_j - xb) for j = 1, 2, 3
# P(Y <= 0) = 0, P(Y <= 4) = 1
pain_level = np.zeros(n, dtype=int)

for i in range(n):
    cum_probs = [logistic(alpha[j] - xb[i]) for j in range(3)]
    # Category probabilities
    p1 = cum_probs[0]               # P(Y=1) = P(Y<=1)
    p2 = cum_probs[1] - cum_probs[0] # P(Y=2) = P(Y<=2) - P(Y<=1)
    p3 = cum_probs[2] - cum_probs[1] # P(Y=3) = P(Y<=3) - P(Y<=2)
    p4 = 1.0 - cum_probs[2]          # P(Y=4) = 1 - P(Y<=3)

    probs = np.array([p1, p2, p3, p4])
    # Clamp to avoid numerical issues
    probs = np.maximum(probs, 0)
    probs = probs / probs.sum()

    pain_level[i] = np.random.choice([1, 2, 3, 4], p=probs)

# --- Build output ---
records = []
for i in range(n):
    records.append({
        "pain_level": int(pain_level[i]),
        "treatment": treatment[i],
        "dose_mg": int(dose_mg[i]),
        "age": int(age[i])
    })

# --- Save ---
output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "data")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "pain-levels.json")

with open(output_path, "w") as f:
    json.dump(records, f, indent=2)

# --- Print summary ---
print(f"Generated {n} observations")
print(f"Saved to {os.path.abspath(output_path)}")
print()
print("Pain level distribution:")
for level in [1, 2, 3, 4]:
    count = np.sum(pain_level == level)
    print(f"  {level} ({['None','Mild','Moderate','Severe'][level-1]}): {count} ({100*count/n:.1f}%)")
print()
print("Treatment distribution:")
for t in treatment_labels:
    count = np.sum(treatment == t)
    print(f"  {t}: {count} ({100*count/n:.1f}%)")
print()
print(f"Age range: {age.min()} - {age.max()}")
print(f"Dose range (non-placebo): {dose_mg[dose_mg > 0].min()} - {dose_mg[dose_mg > 0].max()}")
