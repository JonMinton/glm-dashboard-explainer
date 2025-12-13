# Handover: Optimization Algorithm Refactoring

**Date:** 2025-12-13
**Branch:** feature/claude (uncommitted changes)

## Session Summary

This session made several improvements to the multi-optima visualization:

### Completed Work

1. **Tutorial mode toggle** - Added checkbox that shows labelled annotations:
   - A) Algorithm position (tracks current marker)
   - B) False Peaks (local) - single label with connectors to both Crow Hill and Whinny Hill
   - C) True Peak (global) - Arthur's Seat summit

2. **Real elevation data** - Replaced synthetic data with OS Terrain 50:
   - Created `data/process_os_terrain50.py` for processing downloaded ASC files
   - Added peaks to `docs/data/arthurs_seat_elevation.json` (Arthur's Seat 239.3m, Crow Hill 175.2m, Whinny Hill 139.9m)
   - Fixed ASC parser for variable header lengths

3. **Fixed color scale/contours** - Now use actual data range (14.8m - 239.3m) instead of hardcoded values

4. **Improved Newton-Raphson** - Step size now naturally decreases as gradient approaches zero near optimum

5. **Fixed convergence checks** - Use `elevationData.stats.max - 5` instead of hardcoded 255m

## Next Task: Shared Algorithm Modules

**Goal:** Extract optimization algorithms into shared modules for consistency across tutorials.

### Proposed Architecture

```
docs/js/optimization/
├── algorithms.js      # Gradient ascent, Newton-Raphson, Simulated Annealing, Random Restarts
├── terrain.js         # getElevation(), getGradient() for 2D terrain
└── mcmc.js           # Metropolis-Hastings specific code

scripts/py/optimization/
├── algorithms.py      # Reference implementations (for validation)
└── test_algorithms.py # Test JS matches Python outputs
```

### Implementation Plan

1. **Create shared JS modules:**
   - Extract `getElevation()`, `getGradient()` from multi-optima.html → `terrain.js`
   - Extract `stepGradient()`, `stepNewton()`, `stepAnnealing()`, `stepRandomRestart()` → `algorithms.js`
   - Make algorithms generic (accept objective function, not hardcoded to elevation)

2. **Create Python reference implementations:**
   - `gradient_ascent(f, grad_f, x0, step_size, tol)`
   - `newton_raphson(f, grad_f, hess_f, x0, tol, damping)`
   - `simulated_annealing(f, x0, temp, cooling_rate)`
   - `random_restarts(optimizer, f, n_restarts)`

3. **Update HTML files to import modules:**
   - multi-optima.html: import from shared modules
   - mcmc.html: import terrain.js, keep MCMC-specific code

4. **Add validation tests:**
   - Run same optimization on same terrain in Python and JS
   - Compare trajectories for consistency

### Key Design Decisions

- **JS for interactivity** - Algorithms must run in browser for step-by-step visualization
- **Python for validation** - Reference implementations ensure correctness
- **Generic interfaces** - Algorithms accept objective functions, not tied to elevation
- **ES6 modules** - Use `import/export` syntax (supported in modern browsers)

### Files to Modify

| File | Changes |
|------|---------|
| `docs/optimization/multi-optima.html` | Remove inline algorithms, import modules |
| `docs/optimization/mcmc.html` | Import terrain.js |
| `docs/js/optimization/terrain.js` | NEW: getElevation, getGradient |
| `docs/js/optimization/algorithms.js` | NEW: all optimization algorithms |
| `scripts/py/optimization/algorithms.py` | NEW: Python reference implementations |

### Current Algorithm Implementations

**Gradient Ascent** (stepGradient):
- Fixed step size (0.008)
- Normalizes direction by gradient magnitude
- Converges when |grad| < 0.5

**Newton-Raphson** (stepNewton):
- Computes diagonal Hessian via finite differences
- Uses Newton step when H < -0.1, else gradient fallback
- 0.5 damping factor, 0.08 max step clamp
- Step naturally decreases as grad → 0

**Simulated Annealing** (stepAnnealing):
- Random proposals scaled by temperature
- Metropolis acceptance: exp(ΔE / T)
- Cooling rate 0.995, min temp 0.01

**Random Restarts** (stepRandomRestart):
- 5 restarts, 50 iterations each
- Gradient ascent within each restart
- Tracks best position across all restarts

## Uncommitted Changes

Run `git status` to see current changes. Key modified files:
- `docs/optimization/multi-optima.html` - tutorial mode, NR fix, color scale fix
- `docs/data/arthurs_seat_elevation.json` - added peaks array
- `data/process_os_terrain50.py` - processing script
- `.gitignore` - excludes raw-geo data

## To Resume

1. Commit current changes: `git add -A && git commit -m "..."`
2. Start with creating `docs/js/optimization/terrain.js`
3. Extract and test one algorithm at a time
4. Update HTML files incrementally
