# Tutorial Mode - Guided Script Specification

## Overview

A tutorial version of the model builder that walks users through a predefined example step-by-step. The user must follow the "script" - selecting specific variables in a specific order - before progressing.

## Design Approach

Rather than a completely separate page, we use a **mode parameter** that modifies the same component's behaviour:

- `?mode=explore` (default): Free exploration, any variables allowed
- `?mode=tutorial`: Guided script with highlighting and gating

## Tutorial Script Definition

```javascript
tutorialScript = {
  dataset: "heart",
  title: "Predicting Maximum Heart Rate",
  description: "Learn to build a GLM by predicting thalach (max heart rate) from patient characteristics",

  steps: [
    {
      id: 1,
      instruction: "First, let's select what we want to predict. Drag **Max Heart Rate** to the Response zone.",
      target: { variable: "thalach", zone: "response" },
      hint: "The response variable (y) is what we're trying to explain or predict",
      highlightVariables: ["thalach"],
      blockOthers: true  // Can't drop other variables until this step is done
    },
    {
      id: 2,
      instruction: "Now let's add our first predictor. **Age** is likely to affect heart rate. Drag it to the Predictors zone.",
      target: { variable: "age", zone: "predictor" },
      hint: "Older patients typically have lower maximum heart rates",
      highlightVariables: ["age"],
      blockOthers: true
    },
    {
      id: 3,
      instruction: "Exercise-induced angina might also matter. Add **Exercise Angina** as a predictor.",
      target: { variable: "exang", zone: "predictor" },
      hint: "This is a binary variable - does the patient experience chest pain during exercise?",
      highlightVariables: ["exang"],
      blockOthers: true
    },
    {
      id: 4,
      instruction: "Finally, add **ST Depression** - a measure of heart stress during exercise.",
      target: { variable: "oldpeak", zone: "predictor" },
      hint: "Higher values indicate more cardiac stress",
      highlightVariables: ["oldpeak"],
      blockOthers: true
    },
    {
      id: 5,
      instruction: "Excellent! You've built your first model specification. Click **Continue** to proceed.",
      target: null,  // No drop action needed
      highlightVariables: [],
      blockOthers: false,
      showContinue: true
    }
  ]
}
```

## Visual Differences in Tutorial Mode

### 1. Step Indicator
```
┌────────────────────────────────────────────┐
│  Tutorial: Step 2 of 5                     │
│  ═══════●═══════○═══════○═══════○          │
│                                            │
│  "Now let's add our first predictor..."    │
└────────────────────────────────────────────┘
```

### 2. Variable Highlighting
- Target variable card has **pulsing glow** effect
- Other variable cards are **dimmed** (opacity: 0.4)
- Non-target cards are **not draggable** when `blockOthers: true`

### 3. Drop Zone Highlighting
- Target zone has **pulsing border**
- Wrong zone shows **red flash** if user tries to drop there
- Hint tooltip appears if user hovers wrong zone

### 4. Feedback on Actions
- **Correct drop**: Green checkmark animation, "Well done!" toast, auto-advance to next step
- **Wrong drop**: Gentle shake animation, "Try the highlighted variable" message
- **Skip attempt**: "Complete this step first" message

## CSS Classes for Tutorial Mode

```css
/* Highlighted (target) variable */
.variable-card.tutorial-target {
  animation: pulse-glow 1.5s infinite;
  border-color: var(--bs-success);
  z-index: 10;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 5px var(--bs-success); }
  50% { box-shadow: 0 0 20px var(--bs-success); }
}

/* Dimmed (non-target) variables */
.variable-card.tutorial-dimmed {
  opacity: 0.4;
  pointer-events: none;
  filter: grayscale(50%);
}

/* Target drop zone */
.drop-zone.tutorial-target {
  animation: pulse-border 1.5s infinite;
}

@keyframes pulse-border {
  0%, 100% { border-color: var(--bs-success); }
  50% { border-color: var(--bs-success); border-width: 4px; }
}

/* Wrong action feedback */
.drop-zone.tutorial-wrong {
  animation: shake 0.3s;
  border-color: var(--bs-danger);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
```

## State Management

```javascript
// Tutorial state
mutable tutorialStep = 1
mutable tutorialComplete = false

// Check if current step is satisfied
stepSatisfied = {
  const step = tutorialScript.steps[tutorialStep - 1]
  if (!step.target) return true  // No action needed

  if (step.target.zone === "response") {
    return selectedResponse?.name === step.target.variable
  } else {
    return selectedPredictors.some(p => p.name === step.target.variable)
  }
}

// Auto-advance when step completed
{
  if (stepSatisfied && tutorialStep < tutorialScript.steps.length) {
    // Short delay for feedback animation
    setTimeout(() => {
      mutable tutorialStep = tutorialStep + 1
    }, 800)
  }
}
```

## Implementation Options

### Option A: Query Parameter Mode
Single page with conditional rendering:
```
/pages/model-builder.qmd?mode=tutorial
/pages/model-builder.qmd?mode=explore (or no param)
```

**Pros**: Single codebase, easier maintenance
**Cons**: More complex conditional logic

### Option B: Separate Tutorial Page
Dedicated page that imports shared components:
```
/pages/tutorial/model-builder.qmd  (tutorial mode)
/pages/model-builder.qmd           (explore mode)
```

**Pros**: Cleaner separation, tutorial can have extra narrative
**Cons**: Some code duplication

### Recommendation: Option B with shared components
- Create `/components/variable-canvas.js` with the core logic
- Tutorial page imports it with `tutorialMode: true`
- Explore page imports it with `tutorialMode: false`
- Tutorial page can have additional narrative text, learning objectives, etc.

## Tutorial Page Structure

```markdown
---
title: "Tutorial: Building Your First GLM"
---

## Learning Objectives

By the end of this tutorial, you will be able to:
- Identify response and predictor variables
- Understand the role of each in a linear model
- Build a model specification using the visual canvas

## The Scenario

We have data from 303 patients at Cleveland Clinic. We want to understand
what factors affect a patient's maximum heart rate during exercise.

**Research question:** Can we predict maximum heart rate (thalach) from
patient characteristics?

---

[Interactive Canvas with Tutorial Mode]

---

## What You've Learned

- **Response variable (y)**: The outcome we want to predict (Max Heart Rate)
- **Predictor variables (X)**: Factors that might explain the response
- **Linear predictor**: η = β₀ + β₁·Age + β₂·ExerciseAngina + β₃·STDepression

Next, we'll choose how to transform these predictors and which
distribution family to use.

[Continue to Transforms →]
```

## Questions to Resolve

1. Should users be able to **skip** tutorial steps if they want?
2. Should we show a **"why"** explanation for each variable choice?
3. Should the tutorial have a **restart** button?
4. Should progress be **saved** (localStorage) so users can resume?
