# Handover: 3D Optimization Visualization

## Context

Building a progressive series of optimization visualizations showing how MLE algorithms find the best parameters:
- **1D** (COMPLETE): Estimating a mean - single parameter, 1D likelihood curve
- **2D** (COMPLETE): Linear regression (intercept + slope) - 2D contour surface
- **3D** (IN PROGRESS): Multiple regression (intercept + 2 slopes) - 3D likelihood surface

## Location

All files are in `docs/optimization/`:
- `index.html` - 1D visualization
- `2d.html` - 2D visualization
- `3d.html` - 3D visualization (TO BE CREATED)

## Current Branch

`feature/claude` - ahead of origin by 4 commits

## Design Pattern

Each visualization follows the same structure:
1. **Dual panel layout**: Data + fit (left) | Likelihood surface (right)
2. **Mode toggle**: "Try It Yourself" (manual sliders) vs "Watch Algorithm"
3. **Algorithms**: Analytic, Newton-Raphson, Gradient Descent
4. **Stats display**: Current estimates, log-likelihood, iteration count
5. **Path visualization**: Show algorithm's journey in algorithm mode

## 3D Visualization Plan

### Key Differences from 2D
- 3 parameters: β₀ (intercept), β₁ (slope for x1), β₂ (slope for x2)
- Cannot show full 3D likelihood surface easily - need to slice it
- Options for visualization:
  1. **3D scatter with plane**: Show data points and fitted plane
  2. **2D slices**: Fix one parameter, show contour for other two
  3. **Isosurfaces**: 3D contour levels (complex to implement)

### Recommended Approach
1. **Left panel**: 3D scatter plot of data with fitted plane (use simple isometric projection)
2. **Right panel**: 2D contour slice - user can choose which parameter to fix
3. **Three sliders** for manual mode
4. **Algorithm path** shown on the 2D slice view

### Data Generation
```javascript
// y = β₀ + β₁*x1 + β₂*x2 + noise
// True parameters: β₀=5, β₁=2, β₂=-1
const trueB0 = 5, trueB1 = 2, trueB2 = -1;
for (let i = 0; i < n; i++) {
  const x1 = Math.random() * 10 - 5;
  const x2 = Math.random() * 10 - 5;
  const noise = (Math.random() - 0.5) * 10;
  const y = trueB0 + trueB1 * x1 + trueB2 * x2 + noise;
  data.push({ x1, x2, y });
}
```

### Log-Likelihood
```javascript
function logLikelihood(b0, b1, b2) {
  let ss = 0;
  for (const d of data) {
    const pred = b0 + b1 * d.x1 + b2 * d.x2;
    const resid = d.y - pred;
    ss += resid * resid;
  }
  const sigma2 = 25; // known variance
  return -n/2 * Math.log(2 * Math.PI * sigma2) - ss / (2 * sigma2);
}
```

### Gradient
```javascript
function gradient(b0, b1, b2) {
  let g0 = 0, g1 = 0, g2 = 0;
  const sigma2 = 25;
  for (const d of data) {
    const resid = d.y - (b0 + b1 * d.x1 + b2 * d.x2);
    g0 += resid;
    g1 += resid * d.x1;
    g2 += resid * d.x2;
  }
  return [g0 / sigma2, g1 / sigma2, g2 / sigma2];
}
```

### 3D Scatter Plot (Isometric Projection)
```javascript
function project3D(x1, x2, y) {
  // Simple isometric: x' = x1 - x2, y' = y - 0.5*(x1 + x2)
  const scale = 15;
  const px = centerX + scale * (x1 - x2);
  const py = centerY - scale * (y * 0.8 - 0.3 * (x1 + x2));
  return { x: px, y: py };
}
```

### Gradient Descent Learning Rates
Based on 2D experience, use small adaptive rates:
```javascript
const lr0 = 0.05;  // intercept
const lr1 = 0.01;  // slope 1
const lr2 = 0.01;  // slope 2
```

## Files Modified This Session

1. `docs/optimization/index.html` - Added navigation links, fixed MLE label position
2. `docs/optimization/2d.html` - NEW: Complete 2D visualization

## Commits Made

1. `9bf5763` - Fix MLE label position on likelihood surface
2. `6ff112a` - Add 2D likelihood visualization with contour surface

## Remaining Tasks

1. **Build 3D visualization** (`docs/optimization/3d.html`)
2. **Link from fitting.html pages** to optimization section
3. Consider adding optimization section to main index.html

## Testing

Server running at: `http://localhost:8080/optimization/`
