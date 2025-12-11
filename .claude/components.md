# Component Specifications

## Overview

This document details the interactive components needed for the GLM pedagogy tool.

---

## 1. ScenarioCard

**Purpose**: Display a selectable scenario on Page 1

**Props**:
- `id`: string (e.g., "hospital-readmissions")
- `title`: string
- `description`: string (one sentence)
- `icon`: component/image
- `dataType`: "binary" | "count" | "continuous" | "zero-inflated"
- `suggestedFamily`: string (e.g., "Binomial")

**Behavior**:
- On click: expands slightly, others fade
- Selected state shows checkmark
- "Continue" button appears when one is selected

---

## 2. DataTable

**Purpose**: Paginated display of dataset on Page 2

**Props**:
- `data`: array of objects
- `pageSize`: number (default 20)
- `onColumnSelect`: callback for response/predictor selection

**Features**:
- Column headers show data type indicator
- Click column header to select as Y or X
- Summary row at bottom (N, means, ranges)
- "Quick look" dropdown for single-variable histogram

---

## 3. ModelFlowDiagram

**Purpose**: Central visual showing the GLM data flow

**Structure**:
```
[X₁] ─h₁()→ ┐
[X₂] ─h₂()→ ├─→ [η = Xβ] ─g⁻¹()→ [μ] ─f(·;μ,α)→ [Y]
[X₃] ─h₃()→ ┘                              ↓
                                      [y] (observed)
```

**Interactive Elements**:
- X boxes: show variable name, can have transform dropdown
- h() labels on edges: show selected transform
- η node: shows linear predictor formula
- g⁻¹() node: dropdown for link function selection
- μ node: shows expected value
- f() node: dropdown for distribution family
- Y box: shows "Y ~ Family(μ, α)"
- y box: shows "observed data" with link to actual values

**States**:
- Building (components appear as user selects)
- Complete (all components visible)
- Fitting (β/α values shown on relevant nodes)

---

## 4. TransformSelector

**Purpose**: Dropdown for selecting transformations

**Variants**:
- **PredictorTransform**: [Raw | Log | √ | x² | x³ | Spline]
- **LinkFunction**: [Identity | Log | Logit | Probit | Inverse | Cloglog]
- **DistributionFamily**: [Gaussian | Binomial | Poisson | NegBinomial | Gamma | ZIP]

**Props**:
- `type`: "predictor" | "link" | "distribution"
- `dataType`: string (to filter appropriate options)
- `value`: current selection
- `onChange`: callback
- `showWarnings`: boolean (flag inappropriate choices)

**Features**:
- Tooltip on hover explaining each option
- "Show maths" toggle reveals formula
- Warning icon for unusual combinations

---

## 5. ParameterSlider

**Purpose**: Interactive slider for β or α parameters

**Props**:
- `name`: string (e.g., "β₁", "σ²")
- `label`: string (e.g., "log(length_of_stay)")
- `min`, `max`: number
- `value`: number
- `onChange`: callback
- `parameterType`: "systematic" | "dispersion"

**Features**:
- Blue styling for β (systematic)
- Red styling for α (dispersion)
- Current value displayed
- Reset button
- Lock toggle (for fixing during optimization)

---

## 6. DistributionPlot

**Purpose**: Visualize PDF/PMF for selected distribution

**Props**:
- `family`: string
- `mu`: number (expected value)
- `alpha`: number (dispersion, if applicable)
- `observedValues`: array (optional, to overlay)

**Features**:
- Updates in real-time as μ or α change
- Animate: "If μ = X, here are possible Y values"
- Highlight observed values against theoretical distribution

---

## 7. LikelihoodPanel

**Purpose**: Display and visualize likelihood

**Sections**:

### 7a. LikelihoodValue
- Real-time display: "ℓ(β, α | y) = -234.56"
- Direction indicator (improving/worsening)
- Target value (for gamification)

### 7b. LikelihoodContour
- 2D contour plot for two selected parameters
- Current position marked
- Optimization path traced when algorithm runs
- Click to set parameter values

### 7c. LikelihoodFormula
- Expandable: shows mathematical formula
- Adapts to selected distribution family

---

## 8. OptimizationControls

**Purpose**: Buttons and displays for fitting algorithms

**Props**:
- `availableAlgorithms`: ["IRLS", "Newton-Raphson", "GradientDescent", "NelderMead"]
- `availableLossFunctions`: ["MLE", "LeastSquares", "LAD", "Huber"]
- `onOptimize`: callback

**Features**:
- Algorithm selector dropdown
- Loss function selector dropdown
- "Optimize" button
- Progress display (iterations, convergence status)
- Animate sliders during optimization

---

## 9. DiagnosticsPanel

**Purpose**: Model diagnostic plots

**Plots**:
- Residuals vs Fitted
- Q-Q plot
- Scale-Location
- Residuals vs Leverage

**Features**:
- Linked brushing (hover point → highlight across all plots)
- Badness-of-fit indicator
- Comparison mode (side-by-side models)

---

## 10. ResultsPanel

**Purpose**: Display final fitted model results

**Sections**:
- Coefficient table (estimate, SE, z/t, p-value)
- Dispersion parameter (if applicable)
- Fit statistics (deviance, AIC, BIC)
- Interpretation text (auto-generated)

---

## Page Layouts

### Page 1: Scenario Selection
```
┌────────────────────────────────────────┐
│  What are you trying to understand?    │
├────────┬────────┬────────┬────────────┤
│ Card 1 │ Card 2 │ Card 3 │ Card 4     │
│        │        │        │            │
├────────┴────────┴────────┴────────────┤
│                          [Continue →] │
└────────────────────────────────────────┘
```

### Page 2: Data Exploration
```
┌────────────────────────────────────────┐
│  Your Data: Hospital Readmissions      │
├────────────────────────────────────────┤
│  ┌──────────────────────────────────┐  │
│  │  DataTable (paginated)           │  │
│  │  Click columns to select Y or X  │  │
│  └──────────────────────────────────┘  │
├────────────────────────────────────────┤
│  Summary: N=1024, ...                  │
│                          [Continue →] │
└────────────────────────────────────────┘
```

### Page 3: Model Builder (Interactive Flow)
```
┌────────────────────────────────────────┐
│  Build Your Model                      │
├──────────────┬─────────────────────────┤
│              │                         │
│  Selected    │    ModelFlowDiagram     │
│  Variables   │    (builds up as        │
│              │     user selects)       │
│  Y: [var]    │                         │
│  X: [vars]   │                         │
│              │                         │
├──────────────┴─────────────────────────┤
│                          [Continue →] │
└────────────────────────────────────────┘
```

### Page 4: Fitting
```
┌────────────────────────────────────────┐
│  Tune Your Model                       │
├──────────────┬─────────────────────────┤
│  β Sliders   │   Visualization Panel   │
│  ──────────  │   ┌─────────┬─────────┐ │
│  β₀: [====]  │   │ η dist  │ μ dist  │ │
│  β₁: [====]  │   ├─────────┴─────────┤ │
│  β₂: [====]  │   │  Data vs Model    │ │
│              │   └───────────────────┘ │
│  α Sliders   ├─────────────────────────┤
│  ──────────  │   Likelihood Panel      │
│  σ²: [====]  │   ℓ = -234.56          │
│              │   [Contour plot]        │
├──────────────┼─────────────────────────┤
│ [Optimize]   │   [Results Panel]       │
└──────────────┴─────────────────────────┘
```
