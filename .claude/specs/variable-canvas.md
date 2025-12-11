# Variable Selection Canvas - Component Specification

## Overview

An interactive canvas where users drag variables from a data table to construct their model visually. Variables become moveable nodes that can be designated as response (Y) or predictors (X), and connected to show the model structure.

## User Flow

### Stage 1: Data Table View
- User sees paginated table of the selected dataset
- Each column header is draggable
- Hovering a column shows quick stats (type, range, missing values)

### Stage 2: Drag to Canvas
- User drags a column header onto the canvas area
- The column becomes a **variable node** - a moveable rectangular card showing:
  - Variable name
  - Data type icon (numeric, binary, categorical)
  - Mini distribution visualization (histogram/bar chart)
  - Sample values (first few)

### Stage 3: Designate Response Variable
- User clicks a variable node and selects "Set as Response (y)"
- OR drags variable to a designated "Response" zone on the right
- The node:
  - Moves to the right side of canvas
  - Changes colour (e.g., blue border)
  - Shows label "y (observed)"
  - Only ONE variable can be response; selecting another swaps them

### Stage 4: Designate Predictor Variables
- Remaining variables on canvas are automatically predictors
- User can drag more columns from table
- Predictor nodes:
  - Appear on left side of canvas
  - Show label "X₁", "X₂", etc.
  - Have connection points (right edge)

### Stage 5: Visual Connections
- Lines automatically drawn from each predictor node toward response
- These lines will later show:
  - Transform labels h(X) on the predictor side
  - Converge into η node (linear predictor)
  - Continue through g⁻¹() to μ to Y to y

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  DATA TABLE (collapsible)                                       │
│  ┌────────┬────────┬────────┬────────┬────────┐                │
│  │ age    │ bmi    │ smoker │ charges│ region │  ← draggable   │
│  ├────────┼────────┼────────┼────────┼────────┤    headers     │
│  │ 19     │ 27.9   │ yes    │ 16884  │ SW     │                │
│  │ ...    │ ...    │ ...    │ ...    │ ...    │                │
│  └────────┴────────┴────────┴────────┴────────┘                │
├─────────────────────────────────────────────────────────────────┤
│  CANVAS                                                         │
│                                                                 │
│   ┌─────────┐                                    ┌─────────┐   │
│   │ X₁: age │ ────────────┐                      │         │   │
│   │ [hist]  │             │                      │ y:      │   │
│   └─────────┘             │                      │ charges │   │
│                           ├──────────────────────│ [hist]  │   │
│   ┌─────────┐             │                      │         │   │
│   │ X₂: bmi │ ────────────┤                      └─────────┘   │
│   │ [hist]  │             │                                    │
│   └─────────┘             │                                    │
│                           │                                    │
│   ┌──────────┐            │                                    │
│   │X₃: smoker│ ───────────┘                                    │
│   │ [bar]    │                                                 │
│   └──────────┘                                                 │
│                                                                 │
│   [+ Add more variables from table]                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [Back]                                    [Continue →]         │
└─────────────────────────────────────────────────────────────────┘
```

## Variable Node Component

```
┌─────────────────────┐
│ ≡  age        [X₁]  │  ← drag handle, name, role label
├─────────────────────┤
│ numeric | 18-64     │  ← type and range
├─────────────────────┤
│ ▁▂▃▅▇▅▃▂▁          │  ← mini histogram
├─────────────────────┤
│ 19, 45, 32, 28...   │  ← sample values
├─────────────────────┤
│ [Response] [Remove] │  ← action buttons
└─────────────────────┘
```

## Interactions

| Action | Result |
|--------|--------|
| Drag column header to canvas | Creates new variable node |
| Click "Set as Response" | Moves to right, becomes y |
| Drag node | Repositions on canvas |
| Click "Remove" | Returns variable to table only |
| Drag node back to table | Same as remove |
| Double-click node | Expand to show more details |
| Hover connection line | Highlight the relationship |

## State Management

```javascript
canvasState = {
  response: {
    variable: "charges",
    position: { x: 500, y: 200 }
  },
  predictors: [
    { variable: "age", position: { x: 50, y: 100 }, role: "X₁" },
    { variable: "bmi", position: { x: 50, y: 200 }, role: "X₂" },
    { variable: "smoker", position: { x: 50, y: 300 }, role: "X₃" }
  ],
  connections: [
    // Auto-generated from predictors → response
  ]
}
```

## Validation Rules

1. **Must have exactly one response variable** to proceed
2. **Must have at least one predictor** to proceed
3. **Response cannot be categorical** for Gaussian/Gamma (warn user)
4. **Binary response required** for Binomial (guide user)

## Technical Implementation Options

### Option A: React Flow
- Mature library for node-based UIs
- Built-in drag, zoom, connections
- Custom node components supported
- Quarto can embed via iframe or custom HTML

### Option B: Observable Plot + D3 drag
- Native to Quarto/Observable
- More manual work for connections
- Lighter weight

### Option C: Svelte Flow
- Similar to React Flow
- Smaller bundle size
- Less mature ecosystem

**Recommendation**: Start with **React Flow** for robustness, embed in Quarto page. Can prototype simpler version with Observable first.

## Integration with Next Steps

Once variables are selected, the canvas state flows to:

1. **Model Builder page**: Nodes gain transform dropdowns (h(), g(), f())
2. **Fitting page**: Connection lines show β coefficients
3. **Results page**: Nodes show fitted values, significance

The canvas becomes the persistent visual representation of the model throughout the guided tour.

## Questions to Resolve

1. Should the data table collapse/minimize once variables are on canvas?
2. Allow users to rename variables (aliases)?
3. Show correlation matrix between selected variables?
4. Support for interaction terms (X₁ × X₂)?
