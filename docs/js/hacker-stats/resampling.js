/**
 * Shared resampling routines for the Hacker Stats section
 * (docs/hacker-stats/).
 *
 * Every function that consumes the PRNG is ported 1:1 to Python in
 * scripts/py/validate_hacker_stats.py, so displayed bootstrap CIs and
 * permutation p-values are exactly reproducible outside the browser —
 * same seeds, same index streams, same digits.
 */

import { mulberry32, olsFit, logisticFit } from '../inference/inference-math.js';

export { mulberry32, olsFit, logisticFit };

/** n with-replacement indices, drawn sequentially from rng. */
export function bootstrapIndices(n, rng) {
  const idx = new Array(n);
  for (let i = 0; i < n; i++) idx[i] = Math.floor(rng() * n);
  return idx;
}

/** Fisher-Yates shuffle (returns a new array; rng stream order matters). */
export function fisherYates(values, rng) {
  const arr = values.slice();
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export function mean(values) {
  let s = 0;
  for (const v of values) s += v;
  return s / values.length;
}

/** Sample standard deviation (n - 1 denominator). */
export function sd(values) {
  const m = mean(values);
  let s = 0;
  for (const v of values) s += (v - m) * (v - m);
  return Math.sqrt(s / (values.length - 1));
}

/** Median: midpoint of the two central order statistics for even n. */
export function median(values) {
  const s = values.slice().sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

/** R's default (type 7) interpolating sample quantile. */
export function quantileType7(values, q) {
  const s = values.slice().sort((a, b) => a - b);
  const h = (s.length - 1) * q;
  const lo = Math.floor(h);
  const hi = Math.min(lo + 1, s.length - 1);
  return s[lo] + (h - lo) * (s[hi] - s[lo]);
}

/**
 * Nearest-rank percentile interval over bootstrap statistics.
 * Returns [lo, hi] at the given level (default 95%).
 */
export function percentileCI(statsList, level = 0.95) {
  const s = statsList.slice().sort((a, b) => a - b);
  const b = s.length;
  const alpha = (1 - level) / 2;
  const lo = s[Math.max(0, Math.ceil(alpha * b) - 1)];
  const hi = s[Math.max(0, Math.ceil((1 - alpha) * b) - 1)];
  return [lo, hi];
}

/**
 * Generic bootstrap: resample `n` rows B times, apply statFn to each
 * index array, return the statistics in draw order (caller sorts/CIs).
 * statFn receives the index array so multi-column data can be resampled
 * consistently.
 */
export function bootstrap(n, B, seed, statFn) {
  const rng = mulberry32(seed);
  const out = new Array(B);
  for (let b = 0; b < B; b++) {
    out[b] = statFn(bootstrapIndices(n, rng));
  }
  return out;
}

/** Separation rule for bootstrap logistic refits (shared with Python). */
export function usableLogistic(fit) {
  return fit.converged && Number.isFinite(fit.b1) && Math.abs(fit.b1) <= 15;
}
