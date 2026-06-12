"""
Generate synthetic doctor visits dataset for Tutorial 08: Zero-Inflated Models.

True data-generating process: Zero-Inflated Poisson (ZIP)

Zero-inflation (logistic): logit(pi) = -1.0 - 1.0*has_insurance + 0.04*distance_to_clinic
  pi = probability of being a "structural zero" (never visits regardless)

Count model (Poisson with log link):
  log(mu) = 0.15 + 0.01*age - 0.02*income_10k + 0.5*chronic_condition
  where income_10k = income / 10000

For each observation:
  Draw z ~ Bernoulli(pi): if z=1, y=0 (structural zero)
  If z=0, draw y ~ Poisson(mu) (could still be 0 -- sampling zero)

Target (achieved with seed 42, n=500): 206 zeros (41.2%), of which
144 (28.8%) are structural and 62 are sampling zeros. The count
component has mean mu around 2, so the non-zero distribution is
visibly Poisson-shaped, while a plain Poisson fit badly underpredicts
the number of zeros.

Note: the tutorial pages embed summary statistics inline, so this script
does not write into docs/data/. It saves a CSV to /tmp for use by the
R/Python validation sessions.
"""

import csv
import numpy as np

np.random.seed(42)

n = 500

# Generate predictors
age = np.random.uniform(18, 80, n).round().astype(int)
income = np.random.uniform(15000, 120000, n).round().astype(int)
has_insurance = np.random.binomial(1, 0.65, n)
chronic_condition = np.random.binomial(1, 0.25, n)
distance_to_clinic = np.random.uniform(0.5, 30, n).round(1)

income_10k = income / 10000

# Zero-inflation model (logistic)
logit_pi = -1.0 - 1.0 * has_insurance + 0.04 * distance_to_clinic
pi = 1 / (1 + np.exp(-logit_pi))

# Count model (Poisson with log link)
log_mu = 0.15 + 0.01 * age - 0.02 * income_10k + 0.5 * chronic_condition
mu = np.exp(log_mu)

# Generate response
z = np.random.binomial(1, pi)  # 1 = structural zero
doctor_visits = np.where(z == 1, 0, np.random.poisson(mu))

# Report statistics
n_zeros = (doctor_visits == 0).sum()
pct_zeros = n_zeros / n * 100
hist = np.bincount(doctor_visits)
print(f"Total observations: {n}")
print(f"Total zeros: {n_zeros} ({pct_zeros:.1f}%)")
print(f"Structural zeros: {z.sum()} ({z.sum()/n*100:.1f}%)")
print(f"Sampling zeros (Poisson drew 0): {n_zeros - z.sum()}")
print(f"Mean doctor_visits: {doctor_visits.mean():.2f}")
print(f"Max doctor_visits: {doctor_visits.max()}")
print(f"Histogram (counts for y = 0, 1, 2, ...): {list(hist)}")
print(f"Mean pi (structural zero prob): {pi.mean():.3f}")
print(f"Mean mu (Poisson rate): {mu.mean():.2f}")
print(f"Intercept-only Poisson would predict ~{n * np.exp(-doctor_visits.mean()):.0f} zeros")

# Save CSV for R/Python validation sessions (not part of the site)
output_path = "/tmp/doctor_visits.csv"
with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["age", "income", "has_insurance", "chronic_condition",
                     "distance_to_clinic", "doctor_visits"])
    for i in range(n):
        writer.writerow([age[i], income[i], has_insurance[i], chronic_condition[i],
                         distance_to_clinic[i], doctor_visits[i]])

print(f"\nSaved {n} records to {output_path}")
