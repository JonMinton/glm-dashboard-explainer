#!/usr/bin/env python3
"""
Generate + validate every displayed number for the Hacker Stats section
(docs/hacker-stats/).

House rule: displayed resampling results must be EXACTLY reproducible.
To that end this script ports the site's mulberry32 PRNG (and the
resampling loops that consume it) bit-faithfully from
docs/js/hacker-stats/resampling.js, so bootstrap CIs and permutation
p-values match the browser to the last digit — not just in
distribution.

Also writes docs/data/hacker-bp.json (skewed blood-pressure sample for
the bootstrap median/quantile demo; generation uses numpy seed 777 —
one-off data creation, not resampling).

Run from scripts/py/:  python3 validate_hacker_stats.py
"""

import json
import math

import numpy as np
from scipy import stats

M32 = 0xFFFFFFFF


def mulberry32(seed):
    """Bit-faithful port of the JS mulberry32 in resampling.js."""
    a = seed & M32

    def rng():
        nonlocal a
        a = (a + 0x6D2B79F5) & M32
        t = ((a ^ (a >> 15)) * ((a | 1) & M32)) & M32
        u = ((t ^ (t >> 7)) * ((t | 61) & M32)) & M32
        t = (((t + u) & M32) ^ t) & M32
        return ((t ^ (t >> 14)) & M32) / 4294967296

    return rng


def bootstrap_indices(n, rng):
    return [math.floor(rng() * n) for _ in range(n)]


def fisher_yates(values, rng):
    arr = list(values)
    for i in range(len(arr) - 1, 0, -1):
        j = math.floor(rng() * (i + 1))
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def median(values):
    s = sorted(values)
    n = len(s)
    m = n // 2
    return s[m] if n % 2 else (s[m - 1] + s[m]) / 2


def quantile_type7(values, q):
    """R's default (type 7) interpolating sample quantile."""
    s = sorted(values)
    h = (len(s) - 1) * q
    lo = math.floor(h)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (h - lo) * (s[hi] - s[lo])


def percentile_ci(stats_list, level=0.95):
    """Nearest-rank percentile interval over bootstrap statistics."""
    s = sorted(stats_list)
    b = len(s)
    alpha = (1 - level) / 2
    lo = s[max(0, math.ceil(alpha * b) - 1)]
    hi = s[max(0, math.ceil((1 - alpha) * b) - 1)]
    return lo, hi


def sd(values):
    n = len(values)
    m = sum(values) / n
    return math.sqrt(sum((v - m) ** 2 for v in values) / (n - 1))


def ols_slope(xs, ys):
    n = len(xs)
    xb = sum(xs) / n
    yb = sum(ys) / n
    sxx = sum((x - xb) ** 2 for x in xs)
    sxy = sum((x - xb) * (y - yb) for x, y in zip(xs, ys))
    return sxy / sxx


def _sigmoid_js(z):
    """1/(1+exp(-z)) with JS float semantics: exp overflow -> +inf -> p = 0."""
    try:
        return 1 / (1 + math.exp(-z))
    except OverflowError:
        return 0.0


def logistic_fit(xs, ys, max_iter=50, tol=1e-10):
    """1:1 port of inference-math.js logisticFit (Newton from (0,0))."""
    b0 = b1 = 0.0
    converged = False
    for _ in range(max_iter):
        g0 = g1 = w00 = w01 = w11 = 0.0
        for x, y in zip(xs, ys):
            p = _sigmoid_js(b0 + b1 * x)
            r = y - p
            w = p * (1 - p)
            g0 += r
            g1 += r * x
            w00 += w
            w01 += w * x
            w11 += w * x * x
        det = w00 * w11 - w01 * w01
        if det == 0 or not math.isfinite(det):
            break
        s0 = (w11 * g0 - w01 * g1) / det
        s1 = (w00 * g1 - w01 * g0) / det
        b0 += s0
        b1 += s1
        if not (math.isfinite(b0) and math.isfinite(b1)):
            break
        if abs(s0) < tol and abs(s1) < tol:
            converged = True
            break
    return b0, b1, converged


def usable_logistic(b1, converged):
    """Separation rule shared with the JS: converged and |b1| <= 15."""
    return converged and math.isfinite(b1) and abs(b1) <= 15


# ---------------------------------------------------------------
print("=" * 70)
print("RNG PARITY CHECK: first 5 draws of mulberry32(1)")
print("=" * 70)
r = mulberry32(1)
print([round(r(), 12) for _ in range(5)])

# ---------------------------------------------------------------
with open("../../docs/data/inference-rest-hr.json") as f:
    hr = json.load(f)["data"]
hr_x = [d["x"] for d in hr]
hr_y = [d["y"] for d in hr]

print("\n" + "=" * 70)
print("INDEX DEMO: bootstrap the mean and median of the first 20 heart rates")
print("=" * 70)
y20 = hr_y[:20]
print(f"sample mean {sum(y20)/20:.4f}, sample sd {sd(y20):.4f}, "
      f"theoretical SE = sd/sqrt(20) = {sd(y20)/math.sqrt(20):.4f}")
print(f"sample median {median(y20):.4f}")

for label, statfn, seed in [("mean", lambda v: sum(v) / len(v), 101),
                            ("median", median, 111)]:
    rng = mulberry32(seed)
    boots = []
    for _ in range(1000):
        idx = bootstrap_indices(20, rng)
        boots.append(statfn([y20[i] for i in idx]))
    lo, hi = percentile_ci(boots)
    print(f"bootstrap {label} (B=1000, seed {seed}): "
          f"SE* = {sd(boots):.4f}, 95% percentile CI ({lo:.4f}, {hi:.4f})")

# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("BOOTSTRAP ACT 1: slope of rest-HR (n=60), B=1000, seed 202")
print("=" * 70)
x60, y60 = hr_x[:60], hr_y[:60]
b1_hat = ols_slope(x60, y60)
rng = mulberry32(202)
boots = []
for _ in range(1000):
    idx = bootstrap_indices(60, rng)
    boots.append(ols_slope([x60[i] for i in idx], [y60[i] for i in idx]))
lo, hi = percentile_ci(boots)
print(f"observed slope {b1_hat:.4f}")
print(f"bootstrap SE* = {sd(boots):.4f}  (Wald ML SE was 0.2915)")
print(f"95% percentile CI ({lo:.4f}, {hi:.4f})  (Wald: (-1.8425, -0.6997))")

# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("DATASET: skewed resting blood pressure (hacker-bp.json), seed 777")
print("=" * 70)
gen = np.random.default_rng(777)
N_BP = 80
bp = np.round(90 + gen.gamma(shape=3.0, scale=13.3, size=N_BP)).astype(int)
with open("../../docs/data/hacker-bp.json", "w") as f:
    json.dump(
        {
            "description": "Synthetic resting blood pressure readings (mm Hg), right-skewed: "
                           "90 + Gamma(shape 3, scale 13.3), rounded. Generated by "
                           "scripts/py/validate_hacker_stats.py, numpy seed 777. Companion to "
                           "Tutorial 5's Gamma treatment of blood pressure.",
            "n": N_BP,
            "data": [int(v) for v in bp],
        },
        f,
        indent=1,
    )
bp = [int(v) for v in bp]
print(f"n={N_BP}, mean {sum(bp)/N_BP:.2f}, median {median(bp):.1f}, "
      f"min {min(bp)}, max {max(bp)}, skew {stats.skew(bp):.3f}")

print("\nBOOTSTRAP ACT 2: quantiles of BP, B=1000, seed 303 (same seed each q)")
for q in (0.10, 0.25, 0.50, 0.75, 0.90):
    rng = mulberry32(303)
    boots = []
    for _ in range(1000):
        idx = bootstrap_indices(N_BP, rng)
        boots.append(quantile_type7([bp[i] for i in idx], q))
    lo, hi = percentile_ci(boots)
    print(f"  q{int(q*100):02d}: point {quantile_type7(bp, q):7.2f}   "
          f"95% CI ({lo:.2f}, {hi:.2f})   width {hi-lo:.2f}")

# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("LOGISTIC BOOTSTRAP: biomarker slope (n=30), B=1000, seed 404")
print("=" * 70)
with open("../../docs/data/inference-logistic.json") as f:
    lg = json.load(f)["data"]
lx = [d["x"] for d in lg]
ly = [d["y"] for d in lg]
rng = mulberry32(404)
usable, dropped = [], 0
for _ in range(1000):
    idx = bootstrap_indices(30, rng)
    b0s, b1s, conv = logistic_fit([lx[i] for i in idx], [ly[i] for i in idx])
    if usable_logistic(b1s, conv):
        usable.append(b1s)
    else:
        dropped += 1
lo, hi = percentile_ci(usable)
print(f"separated/non-converged resamples: {dropped} of 1000")
print(f"usable resamples: {len(usable)}; 95% percentile CI ({lo:.4f}, {hi:.4f})")
print("(Wald: (0.7425, 4.1233); flat-prior credible: (1.3720, 5.5291))")

# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("CARDS PERMUTATION (JonStats' two coins): 9/12 red vs 3/8 blue")
print("=" * 70)
cards = [1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1,   # red: 9 heads of 12
         0, 1, 0, 0, 1, 0, 1, 0]               # blue: 3 heads of 8
obs = sum(cards[:12]) / 12 - sum(cards[12:]) / 8
print(f"observed difference in proportions: {obs:.4f} (0.750 - 0.375)")
rng = mulberry32(505)
extreme = 0
for _ in range(1000):
    shuffled = fisher_yates(cards, rng)
    diff = sum(shuffled[:12]) / 12 - sum(shuffled[12:]) / 8
    if diff >= obs - 1e-12:
        extreme += 1
print(f"one-sided permutation p (B=1000, seed 505): {extreme}/1000 = {extreme/1000:.3f}")
p_exact = stats.hypergeom.sf(8, 20, 12, 12)  # P(red heads >= 9)
print(f"exact (Fisher one-sided): {p_exact:.4f}  (JonStats quotes 0.113)")

# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("PROPORTION BOOTSTRAP (comparison.html scenario c): 2 of 20, seed 707")
print("=" * 70)
events = [1, 1] + [0] * 18
rng = mulberry32(707)
boots = []
for _ in range(1000):
    idx = bootstrap_indices(20, rng)
    boots.append(sum(events[i] for i in idx) / 20)
lo, hi = percentile_ci(boots)
print(f"observed p-hat = 0.100; bootstrap 95% percentile CI ({lo:.3f}, {hi:.3f})")
print("(Wald: (-0.031, 0.231) — leaks below 0; credible: (0.031, 0.304))")

# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("SLOPE PERMUTATION: shuffle y in rest-HR (n=60), B=1000, seed 606")
print("=" * 70)
rng = mulberry32(606)
extreme = 0
null_slopes = []
for _ in range(1000):
    ys_perm = fisher_yates(y60, rng)
    s = ols_slope(x60, ys_perm)
    null_slopes.append(s)
    if abs(s) >= abs(b1_hat) - 1e-12:
        extreme += 1
print(f"observed slope {b1_hat:.4f}; null sd {sd(null_slopes):.4f}")
print(f"two-sided permutation p: {extreme}/1000 "
      f"-> {'p < 0.001' if extreme == 0 else f'{extreme/1000:.3f}'}")

# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("POST-STRATIFICATION DEMO (poststratification.html)")
print("=" * 70)
# Cells in fixed order: young men, young women, older men, older women
POP_SHARE = [0.18, 0.19, 0.30, 0.33]
SUPPORT = [0.30, 0.45, 0.55, 0.65]
GAMER_SHARE = [0.60, 0.15, 0.18, 0.07]
TRUTH = sum(p * s for p, s in zip(POP_SHARE, SUPPORT))
print(f"population truth: {TRUTH:.4f}")


def sample_shares(lam):
    return [(1 - lam) * p + lam * g for p, g in zip(POP_SHARE, GAMER_SHARE)]


def expected_estimates(lam):
    s = sample_shares(lam)
    naive = sum(sh * p for sh, p in zip(s, SUPPORT))
    # gender-only: cells (0,2)=men, (1,3)=women
    men_s = s[0] + s[2]
    women_s = s[1] + s[3]
    p_men = (s[0] * SUPPORT[0] + s[2] * SUPPORT[2]) / men_s
    p_wom = (s[1] * SUPPORT[1] + s[3] * SUPPORT[3]) / women_s
    gender_only = (POP_SHARE[0] + POP_SHARE[2]) * p_men + (POP_SHARE[1] + POP_SHARE[3]) * p_wom
    # age-only: cells (0,1)=young, (2,3)=older
    young_s = s[0] + s[1]
    older_s = s[2] + s[3]
    p_young = (s[0] * SUPPORT[0] + s[1] * SUPPORT[1]) / young_s
    p_older = (s[2] * SUPPORT[2] + s[3] * SUPPORT[3]) / older_s
    age_only = (POP_SHARE[0] + POP_SHARE[1]) * p_young + (POP_SHARE[2] + POP_SHARE[3]) * p_older
    return naive, gender_only, age_only


for lam in (0.0, 0.5, 1.0):
    naive, gonly, aonly = expected_estimates(lam)
    print(f"idealised, bias={lam:.1f}: naive {naive:.4f}, "
          f"poststrat(gender only) {gonly:.4f}, poststrat(age only) {aonly:.4f}, "
          f"poststrat(both) {TRUTH:.4f}")


def simulate(lam, seed=808, n=1000):
    """Seeded draw shared 1:1 with the page's JS (mulberry32 stream order)."""
    s = sample_shares(lam)
    cum = [s[0], s[0] + s[1], s[0] + s[1] + s[2], 1.0]
    rng = mulberry32(seed)
    cell_n = [0, 0, 0, 0]
    cell_y = [0, 0, 0, 0]
    for _ in range(n):
        u1 = rng()
        g = 0
        while u1 >= cum[g]:
            g += 1
        u2 = rng()
        cell_n[g] += 1
        if u2 < SUPPORT[g]:
            cell_y[g] += 1
    naive = sum(cell_y) / n
    post = sum(POP_SHARE[g] * (cell_y[g] / cell_n[g]) for g in range(4))
    return naive, post, cell_n


for lam in (0.5, 1.0):
    naive, post, cell_n = simulate(lam)
    print(f"seeded n=1000 (seed 808), bias={lam:.1f}: naive {naive:.4f}, "
          f"poststrat(both) {post:.4f}, cell counts {cell_n}")

print("\nDone. docs/data/hacker-bp.json written.")
