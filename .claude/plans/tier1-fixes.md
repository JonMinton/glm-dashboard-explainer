# Tier 1: Fix Errors — Implementation Plan

## Overview
Six concrete bugs to fix. All are in existing files. No new files needed.
Estimated effort: one focused session.

---

## Fix 1.1 — 1D Gradient Descent: Sign Descent -> Real Gradient Descent

**File**: `docs/optimization/index.html` (~line 1110-1120)

**Problem**: Uses `Math.sign(grad)` instead of actual gradient value. Takes constant-size steps regardless of gradient steepness. Not gradient descent — it's sign descent.

**Fix**:
```js
// BEFORE (wrong):
currentEstimate = currentEstimate + stepSize * Math.sign(grad);

// AFTER (correct):
// Use gradient directly with a learning rate
const learningRate = 0.5;  // tune for visual speed
currentEstimate = currentEstimate + learningRate * grad;
```

**Considerations**:
- The learning rate needs tuning so the animation looks good (not too fast, not too slow)
- May need to clamp step size to prevent overshooting: `Math.max(-maxStep, Math.min(maxStep, learningRate * grad))`
- Test with all three distributions (Gaussian, Poisson, Binomial) that the 1D page supports

**Verification**: Run the page, click gradient descent, confirm smooth convergence (steps shrink near optimum) instead of constant-size jumps.

---

## Fix 1.2 — Gamma IRLS Weight in Comparison Table

**File**: `docs/tutorials/03-poisson/advanced.html` (~line 533)

**Problem**: Table shows Gamma+log link has IRLS weight W_ii = mu_i^2. Correct value is 1 (constant).

**Fix**: In the HTML table, change the Gamma weights cell:
```html
<!-- BEFORE -->
<td>$\mu_i^2$</td>

<!-- AFTER -->
<td>$1$ (constant)</td>
```

Optionally add a footnote after the table:
```html
<p style="font-size: 0.85em; color: #888;">
  Note: With the canonical inverse link (g(mu) = 1/mu), the Gamma weights would be mu_i^2.
  The log link gives constant weights because (d mu/d eta)^2 / V(mu) = mu^2 / mu^2 = 1.
</p>
```

**Verification**: Visual check that the table renders correctly with KaTeX.

---

## Fix 1.3 — Newton-Raphson: Use Full 2x2 Hessian

**File**: `docs/js/optimization/algorithms.js` (~lines 97-155)

**Problem**: Uses only diagonal Hessian (fxx, fyy), ignoring cross-derivative fxy. Gives wrong steps on rotated landscapes.

**Fix**:

1. Update the import at the top of the file:
```js
// BEFORE:
import { getGradient, getHessianDiag, gradientMagnitude } from './terrain.js';

// AFTER:
import { getGradient, getFullHessian, gradientMagnitude } from './terrain.js';
```

2. Replace the Newton step computation (~lines 113-139):
```js
// Get full 2x2 Hessian
const hess = getFullHessian(terrainData, state.x, state.y, h);

// Compute Newton step using full 2x2 inverse
// H^{-1} = (1/det) * [[fyy, -fxy], [-fxy, fxx]]
const det = hess.fxx * hess.fyy - hess.fxy * hess.fxy;

let stepX, stepY;

// Check if Hessian is well-conditioned and negative definite
if (det > 0 && hess.fxx < opts.hessianThreshold) {
  // Full Newton step: -H^{-1} * grad
  stepX = -(hess.fyy * grad.dx - hess.fxy * grad.dy) / det;
  stepY = -(hess.fxx * grad.dy - hess.fxy * grad.dx) / det;
} else {
  // Ill-conditioned: fall back to gradient ascent
  stepX = grad.dx * opts.fallbackStepSize;
  stepY = grad.dy * opts.fallbackStepSize;
}

// Apply damping
stepX *= opts.damping;
stepY *= opts.damping;

// Safety clamp
stepX = clamp(stepX, -opts.maxStep, opts.maxStep);
stepY = clamp(stepY, -opts.maxStep, opts.maxStep);
```

3. Update the return object to include full Hessian:
```js
hessian: hess,  // now has {fxx, fyy, fxy}
```

**Also update Python mirror**: `scripts/py/optimization/algorithms.py` — update `step_newton_raphson` with equivalent logic using `get_full_hessian` (which would need adding to the TerrainFunction class).

**Verification**:
- Test on `'simple-peak'` preset — should converge similarly to before
- Test on `'asymmetric-peak'` and `'sharp-ridge'` presets — should converge faster/more directly than before
- Run `scripts/py/optimization/test_consistency.py` (after updating Python) — Newton should still pass convergence tests
- Check multi-optima.html and mcmc.html still work (they import from algorithms.js)

---

## Fix 1.4 — MCMC: Reject Out-of-Bounds Proposals Instead of Clamping

**File**: `docs/js/optimization/algorithms.js` (~lines 434-439)

**Problem**: Proposals outside [0,1] are clamped, breaking detailed balance.

**Fix**: Replace clamping with rejection:
```js
// BEFORE:
const clampedX = Math.max(0.01, Math.min(0.99, proposedX));
const clampedY = Math.max(0.01, Math.min(0.99, proposedY));
const proposedElevation = getElev(clampedX, clampedY);

// AFTER:
// Reject out-of-bounds proposals to preserve detailed balance
if (proposedX < 0 || proposedX > 1 || proposedY < 0 || proposedY > 1) {
  return {
    ...state,
    iteration: state.iteration + 1,
    accepted: false,
    proposedX,
    proposedY,
    proposedElevation: null,
    logAcceptRatio: -Infinity,
  };
}

const proposedElevation = getElev(proposedX, proposedY);
```

**Also update Python mirror**: Same logic in `step_mcmc()`.

**Verification**:
- Open mcmc.html, run chains — acceptance rate may drop slightly near edges, which is correct
- Chains should still explore the space and concentrate around peaks
- R-hat should still converge

---

## Fix 1.5 — Tutorial 4 Python: Remove Hardcoded Alpha

**File**: `docs/tutorials/04-negbin/code.html` (~line 397)

**Problem**: Python code passes `alpha=1/6.773` directly instead of estimating it.

**Fix**: Find the Python code block and change:
```python
# BEFORE:
family=sm.families.NegativeBinomial(alpha=1/6.773)

# AFTER:
family=sm.families.NegativeBinomial()
```

Then add a comment after the fit showing how to extract the estimated alpha:
```python
# Extract estimated dispersion parameter
print(f"Estimated alpha: {fit_nb.scale:.4f}")
```

**Important**: The expected output section below the code will likely need updating. The coefficients should be very similar but SEs may differ slightly. Ideally re-run the code to get exact values, but if not possible, add a note that values are approximate.

**Verification**: If Python + statsmodels available locally, run the code to verify output. Otherwise, flag the expected output as needing re-validation.

---

## Fix 1.6 — 2D Gradient Descent: Adaptive Learning Rates

**File**: `docs/optimization/2d.html` (~lines 1002-1012)

**Problem**: Fixed learning rates (lr0=0.1, lr1=0.02) don't adapt to problem conditioning.

**Fix**: Normalize the gradient and use a single step size (matching the pattern in algorithms.js):
```js
// BEFORE:
const lr0 = 0.1;
const lr1 = 0.02;
currentIntercept += lr0 * g0;
currentSlope += lr1 * g1;

// AFTER:
const magnitude = Math.sqrt(g0 * g0 + g1 * g1);
if (magnitude < convergenceTol) {
  // Converged
  break;
}
const stepSize = 0.5;  // tune for visual speed
currentIntercept += stepSize * (g0 / magnitude);
currentSlope += stepSize * (g1 / magnitude);
```

**Consideration**: The intercept and slope have very different scales (intercept ~100-200, slope ~0-5). The step size may need to be in the original parameter units, not normalized. An alternative approach:
```js
// Scale step by parameter ranges
const interceptRange = paramRanges.intercept.max - paramRanges.intercept.min;
const slopeRange = paramRanges.slope.max - paramRanges.slope.min;
const stepFraction = 0.01;  // move ~1% of range per step
currentIntercept += stepFraction * interceptRange * (g0 / magnitude);
currentSlope += stepFraction * slopeRange * (g1 / magnitude);
```

**Verification**: Run the 2D page, click gradient descent from various starting points, confirm:
- Convergence is smooth (no oscillation)
- Speed is visually reasonable
- Works for different datasets

---

## Execution Order

```
1.2 (trivial table fix)
  |
1.1 (1D gradient descent)
  |
1.6 (2D gradient descent)
  |
1.3 (Newton-Raphson full Hessian)  <- most complex, needs testing
  |
1.4 (MCMC boundary rejection)     <- same file as 1.3
  |
1.5 (NegBin Python alpha)         <- last, may need output re-validation
```

Start with the trivial fix (1.2) to build momentum.
Do 1.3 and 1.4 together since they touch the same file.
End with 1.5 since it may need manual verification.

---

## Post-Tier-1 Checkpoint

After all fixes are committed, verify:
- [ ] All optimization pages load without JS errors (browser console)
- [ ] Gradient descent (1D) shows smooth convergence
- [ ] Gradient descent (2D) converges without oscillation
- [ ] Newton-Raphson converges faster on rotated terrains
- [ ] MCMC chains explore the space (mcmc.html)
- [ ] Multi-optima comparison still works
- [ ] Poisson advanced page table renders correctly
- [ ] Tutorial 4 Python code doesn't have hardcoded alpha

Then decide on Tier 2 priorities.
