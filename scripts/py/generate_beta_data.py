"""
Generate synthetic exam proportions dataset for Beta regression tutorial.

DGP: logit(mu) = -3.5 + 0.12*study_hours + 1.0*prior_gpa + 0.4*has_tutor
     phi (precision) = 25
     y ~ Beta(mu*phi, (1-mu)*phi)
"""

import numpy as np
import json
import os

np.random.seed(42)

n = 250

# Predictors
study_hours = np.round(np.random.uniform(1, 20, n), 1)
prior_gpa = np.round(np.random.uniform(2.0, 4.0, n), 2)
has_tutor = np.random.binomial(1, 0.3, n)

# True model
eta = -3.5 + 0.12 * study_hours + 1.0 * prior_gpa + 0.4 * has_tutor
mu = 1.0 / (1.0 + np.exp(-eta))

# Beta distribution parameters
phi = 25
alpha = mu * phi
beta_param = (1 - mu) * phi

# Generate response
y = np.random.beta(alpha, beta_param)

# Clip to (0.01, 0.99) to ensure valid Beta support
y = np.clip(y, 0.01, 0.99)
proportion_correct = np.round(y, 4)

# Build records
records = []
for i in range(n):
    records.append({
        "study_hours": float(study_hours[i]),
        "prior_gpa": float(prior_gpa[i]),
        "has_tutor": int(has_tutor[i]),
        "proportion_correct": float(proportion_correct[i])
    })

# Save
out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "data")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "exam-proportions.json")

with open(out_path, "w") as f:
    json.dump(records, f, indent=2)

print(f"Saved {n} records to {out_path}")
print(f"proportion_correct range: [{min(proportion_correct):.4f}, {max(proportion_correct):.4f}]")
print(f"proportion_correct mean: {np.mean(proportion_correct):.4f}")
