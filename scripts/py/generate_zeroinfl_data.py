"""
Generate synthetic doctor visits dataset for Tutorial 08: Zero-Inflated Models.

True data-generating process: Zero-Inflated Poisson (ZIP)

Zero-inflation (logistic): logit(pi) = 1.2 - 1.5*has_insurance + 0.05*distance_to_clinic
  pi = probability of being a "structural zero" (never visits regardless)

Count model (Poisson with log link): log(mu) = 0.3 + 0.01*age - 0.000005*income + 0.7*chronic_condition

For each observation:
  Draw z ~ Bernoulli(pi): if z=1, y=0 (structural zero)
  If z=0, draw y ~ Poisson(mu) (could still be 0 -- sampling zero)

Target: approximately 35-45% zeros in the data
"""

import numpy as np
import json
import os

np.random.seed(42)

n = 500

# Generate predictors
age = np.random.uniform(18, 80, n).round().astype(int)
income = np.random.uniform(15000, 120000, n).round().astype(int)
has_insurance = np.random.binomial(1, 0.65, n)
chronic_condition = np.random.binomial(1, 0.25, n)
distance_to_clinic = np.random.uniform(0.5, 30, n).round(1)

# Zero-inflation model (logistic)
logit_pi = 1.2 - 1.5 * has_insurance + 0.05 * distance_to_clinic
pi = 1 / (1 + np.exp(-logit_pi))

# Count model (Poisson with log link)
log_mu = 0.3 + 0.01 * age - 0.000005 * income + 0.7 * chronic_condition
mu = np.exp(log_mu)

# Generate response
z = np.random.binomial(1, pi)  # 1 = structural zero
doctor_visits = np.where(z == 1, 0, np.random.poisson(mu))

# Report statistics
n_zeros = (doctor_visits == 0).sum()
pct_zeros = n_zeros / n * 100
print(f"Total observations: {n}")
print(f"Total zeros: {n_zeros} ({pct_zeros:.1f}%)")
print(f"Structural zeros: {z.sum()} ({z.sum()/n*100:.1f}%)")
print(f"Sampling zeros (Poisson drew 0): {n_zeros - z.sum()}")
print(f"Mean doctor_visits: {doctor_visits.mean():.2f}")
print(f"Max doctor_visits: {doctor_visits.max()}")
print(f"Mean pi (structural zero prob): {pi.mean():.3f}")
print(f"Mean mu (Poisson rate): {mu.mean():.2f}")

# Build JSON array of objects
data = []
for i in range(n):
    data.append({
        "age": int(age[i]),
        "income": int(income[i]),
        "has_insurance": int(has_insurance[i]),
        "chronic_condition": int(chronic_condition[i]),
        "distance_to_clinic": float(distance_to_clinic[i]),
        "doctor_visits": int(doctor_visits[i])
    })

# Save to docs/data/doctor-visits.json
output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'data')
output_path = os.path.join(output_dir, 'doctor-visits.json')
os.makedirs(output_dir, exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"\nSaved {len(data)} records to {output_path}")
