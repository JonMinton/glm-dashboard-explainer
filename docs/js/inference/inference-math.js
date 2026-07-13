/**
 * Shared numerical routines for the Statistical Inference section
 * (docs/inference/).
 *
 * Everything here is deterministic given its inputs; displayed numbers are
 * cross-validated against scripts/py/generate_inference_data.py and
 * scripts/R/validate-inference.R (both seed 42).
 *
 * Conventions match docs/js/optimization/terrain.js: Hessians are of the
 * LOG-LIKELIHOOD (maximised, so negative definite at the peak), expressed
 * as {fxx, fyy, fxy}.
 */

/** Deterministic 32-bit PRNG (Mulberry32) so interactive draws are reproducible. */
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Standard normal draw via Box-Muller, using the supplied uniform RNG. */
export function randnFrom(rng) {
  let u = 0, v = 0;
  while (u === 0) u = rng();
  while (v === 0) v = rng();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

/**
 * Ordinary least squares fit of y = b0 + b1 x.
 * Returns both the ML sigma^2 (divide by n) and the OLS/df-corrected
 * sigma^2 (divide by n-2), since the pages discuss the difference.
 */
export function olsFit(xs, ys) {
  const n = xs.length;
  const xBar = xs.reduce((s, v) => s + v, 0) / n;
  const yBar = ys.reduce((s, v) => s + v, 0) / n;
  let sxx = 0, sxy = 0;
  for (let i = 0; i < n; i++) {
    sxx += (xs[i] - xBar) * (xs[i] - xBar);
    sxy += (xs[i] - xBar) * (ys[i] - yBar);
  }
  const b1 = sxy / sxx;
  const b0 = yBar - b1 * xBar;
  let rss = 0, sumX = 0, sumX2 = 0;
  for (let i = 0; i < n; i++) {
    const r = ys[i] - (b0 + b1 * xs[i]);
    rss += r * r;
    sumX += xs[i];
    sumX2 += xs[i] * xs[i];
  }
  return {
    n, b0, b1,
    sigma2ML: rss / n,
    sigma2OLS: rss / (n - 2),
    sumX, sumX2, rss,
  };
}

/**
 * Hessian of the Gaussian profile log-likelihood in (b0, b1), with sigma^2
 * held at the value supplied (usually the ML estimate): H = -X'X / sigma^2.
 */
export function gaussianProfileHessian(fit, sigma2) {
  return {
    fxx: -fit.n / sigma2,
    fyy: -fit.sumX2 / sigma2,
    fxy: -fit.sumX / sigma2,
  };
}

/** Gaussian log-likelihood of a line (b0, b1) with dispersion sigma2. */
export function gaussianLL(xs, ys, b0, b1, sigma2) {
  const n = xs.length;
  let rss = 0;
  for (let i = 0; i < n; i++) {
    const r = ys[i] - (b0 + b1 * xs[i]);
    rss += r * r;
  }
  return -0.5 * n * Math.log(2 * Math.PI * sigma2) - rss / (2 * sigma2);
}

/** Invert a symmetric 2x2 matrix given as {fxx, fyy, fxy}. */
export function invertSym2x2(m) {
  const det = m.fxx * m.fyy - m.fxy * m.fxy;
  if (det === 0) return null;
  return { fxx: m.fyy / det, fyy: m.fxx / det, fxy: -m.fxy / det };
}

/**
 * Variance-covariance matrix from a log-likelihood Hessian at the peak:
 * negate (observed information), then invert.
 * Returns {v00, v11, v01, se0, se1} or null if the Hessian is not a valid maximum.
 */
export function hessianToVcov(hessian) {
  const info = { fxx: -hessian.fxx, fyy: -hessian.fyy, fxy: -hessian.fxy };
  if (info.fxx <= 0 || info.fyy <= 0) return null;
  const det = info.fxx * info.fyy - info.fxy * info.fxy;
  if (det <= 0) return null;
  const inv = invertSym2x2(info);
  return {
    v00: inv.fxx, v11: inv.fyy, v01: inv.fxy,
    se0: Math.sqrt(inv.fxx), se1: Math.sqrt(inv.fyy),
  };
}

/**
 * Draw nDraws points from MVN(mean, cov) via the Cholesky factor of the
 * 2x2 covariance. cov as {v00, v11, v01}.
 */
export function mvnDraws(mean, cov, nDraws, rng) {
  const l11 = Math.sqrt(cov.v00);
  const l21 = cov.v01 / l11;
  const l22 = Math.sqrt(Math.max(cov.v11 - l21 * l21, 1e-12));
  const draws = [];
  for (let i = 0; i < nDraws; i++) {
    const z1 = randnFrom(rng);
    const z2 = randnFrom(rng);
    draws.push({
      x: mean.x + l11 * z1,
      y: mean.y + l21 * z1 + l22 * z2,
    });
  }
  return draws;
}

/** Weighted quantile over an ordered grid: smallest gridpoint with CDF >= q. */
export function gridQuantile(gridValues, weights, q) {
  let cum = 0;
  for (let i = 0; i < gridValues.length; i++) {
    cum += weights[i];
    if (cum >= q) return gridValues[i];
  }
  return gridValues[gridValues.length - 1];
}

/**
 * Flat-prior posterior for a binomial proportion on a fine grid.
 * Returns {ps, dens} with dens normalised to sum to 1.
 */
export function binomialGridPosterior(y, n, points = 2000) {
  const ps = [], logDens = [];
  let maxLog = -Infinity;
  for (let i = 0; i < points; i++) {
    const p = (i + 0.5) / points * 0.999 + 0.0005;
    const ld = y * Math.log(p) + (n - y) * Math.log(1 - p);
    ps.push(p);
    logDens.push(ld);
    if (ld > maxLog) maxLog = ld;
  }
  let total = 0;
  const dens = logDens.map(ld => {
    const d = Math.exp(ld - maxLog);
    total += d;
    return d;
  });
  return { ps, dens: dens.map(d => d / total) };
}

/** Log-likelihood of a simple logistic regression logit(p) = b0 + b1 x. */
export function logisticLL(xs, ys, b0, b1) {
  let ll = 0;
  for (let i = 0; i < xs.length; i++) {
    const eta = b0 + b1 * xs[i];
    // Numerically stable: -log(1+e^-eta) for y=1, -log(1+e^eta) for y=0
    ll += ys[i] === 1
      ? (eta > 30 ? 0 : -Math.log1p(Math.exp(-eta)))
      : (eta < -30 ? 0 : -Math.log1p(Math.exp(eta)));
  }
  return ll;
}

/**
 * Fit logistic regression by Newton-Raphson from (0,0).
 * Returns {b0, b1, hessian, vcov, converged} where hessian is the Hessian
 * of the log-likelihood at the MLE ({fxx, fyy, fxy}, negative definite).
 */
export function logisticFit(xs, ys, maxIter = 50, tol = 1e-10) {
  let b0 = 0, b1 = 0;
  let converged = false;
  let H = null;
  for (let iter = 0; iter < maxIter; iter++) {
    let g0 = 0, g1 = 0, w00 = 0, w01 = 0, w11 = 0;
    for (let i = 0; i < xs.length; i++) {
      const p = 1 / (1 + Math.exp(-(b0 + b1 * xs[i])));
      const r = ys[i] - p;
      const w = p * (1 - p);
      g0 += r;
      g1 += r * xs[i];
      w00 += w;
      w01 += w * xs[i];
      w11 += w * xs[i] * xs[i];
    }
    H = { fxx: -w00, fyy: -w11, fxy: -w01 };
    const det = w00 * w11 - w01 * w01;
    const step0 = (w11 * g0 - w01 * g1) / det;
    const step1 = (w00 * g1 - w01 * g0) / det;
    b0 += step0;
    b1 += step1;
    if (Math.abs(step0) < tol && Math.abs(step1) < tol) { converged = true; break; }
  }
  return { b0, b1, hessian: H, vcov: hessianToVcov(H), converged };
}

/**
 * Flat-prior grid posterior for simple logistic regression over
 * (b0, b1), spanning centre +/- span * se in each direction with G points.
 * Mirrors scripts/py/generate_inference_data.py exactly (G=240, span=6).
 * Returns marginals and a joint density grid for heatmap drawing.
 */
export function logisticGridPosterior(xs, ys, centre, ses, G = 240, span = 6) {
  const b0s = [], b1s = [];
  for (let i = 0; i < G; i++) {
    b0s.push(centre.b0 - span * ses.se0 + (2 * span * ses.se0) * i / (G - 1));
    b1s.push(centre.b1 - span * ses.se1 + (2 * span * ses.se1) * i / (G - 1));
  }
  const logJoint = new Float64Array(G * G);
  let maxLog = -Infinity;
  for (let i = 0; i < G; i++) {
    for (let j = 0; j < G; j++) {
      const ll = logisticLL(xs, ys, b0s[i], b1s[j]);
      logJoint[i * G + j] = ll;
      if (ll > maxLog) maxLog = ll;
    }
  }
  const joint = new Float64Array(G * G);
  let total = 0;
  for (let k = 0; k < G * G; k++) {
    joint[k] = Math.exp(logJoint[k] - maxLog);
    total += joint[k];
  }
  const marg0 = new Float64Array(G);
  const marg1 = new Float64Array(G);
  for (let i = 0; i < G; i++) {
    for (let j = 0; j < G; j++) {
      const w = joint[i * G + j] / total;
      marg0[i] += w;
      marg1[j] += w;
    }
  }
  const q = (grid, marg, qq) => gridQuantile(grid, marg, qq);
  const sd = (grid, marg) => {
    let m = 0, m2 = 0;
    for (let i = 0; i < G; i++) { m += marg[i] * grid[i]; m2 += marg[i] * grid[i] * grid[i]; }
    return Math.sqrt(m2 - m * m);
  };
  return {
    b0s, b1s, joint, total,
    b0: { lo: q(b0s, marg0, 0.025), med: q(b0s, marg0, 0.5), hi: q(b0s, marg0, 0.975), sd: sd(b0s, marg0), marg: marg0 },
    b1: { lo: q(b1s, marg1, 0.025), med: q(b1s, marg1, 0.5), hi: q(b1s, marg1, 0.975), sd: sd(b1s, marg1), marg: marg1 },
  };
}

/**
 * Random-walk Metropolis on an arbitrary log-density, for the "walked
 * portrait" of the posterior. Returns the chain (post burn-in).
 */
export function metropolis(logDensity, start, proposalSd, nSteps, rng, burnIn = 200) {
  let cur = { ...start };
  let curLog = logDensity(cur.x, cur.y);
  const samples = [];
  let accepted = 0;
  for (let i = 0; i < nSteps + burnIn; i++) {
    const prop = {
      x: cur.x + proposalSd.x * randnFrom(rng),
      y: cur.y + proposalSd.y * randnFrom(rng),
    };
    const propLog = logDensity(prop.x, prop.y);
    if (Math.log(rng()) < propLog - curLog) {
      cur = prop;
      curLog = propLog;
      accepted++;
    }
    if (i >= burnIn) samples.push({ ...cur });
  }
  return { samples, acceptanceRate: accepted / (nSteps + burnIn) };
}
