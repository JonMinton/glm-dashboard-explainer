# Future Session Areas for GLM Dashboard Explainer

Based on the JonStats pedagogical approach (GLMs as the unifying framework, simulation-based learning, "Statistics as Circuit Boards" metaphor) and the current state of the project.

---

## 1. Simulation-Based Inference Visualiser

**Concept**: Interactive demonstration of how simulation can be used to understand sampling distributions and inference.

**Why it fits**: JonStats emphasises "Likelihood and Simulation Theory" as a core module. The current optimisation visualisations show how algorithms find parameters; this would show what happens *after* we have estimates.

**Key features**:
- Generate data from a known GLM (user picks family/link/true parameters)
- Fit the model, get point estimates
- Bootstrap/simulate many samples → show sampling distribution of β̂
- Compare to asymptotic normal approximation (Wald intervals)
- Show coverage probability in real-time: "Of 100 simulated 95% CIs, X actually contain the true value"

**Technical approach**: Similar dual-panel layout. Left: data generation. Right: sampling distribution building up as simulation runs.

**Links to existing work**: Could extend from the optimization section - "Now that we've found the MLE, how certain are we?"

---

## 2. Loss Functions Compared

**Concept**: Side-by-side comparison of different loss functions (MLE/deviance, OLS, LAD, Huber) showing why MLE is "special" for GLMs.

**Why it fits**: The claude-concept-chat explicitly discusses this: "maximum likelihood is one of many theoretically possible loss functions, though one which can be strongly demonstrated from first principles."

**Key features**:
- Same data, multiple loss functions
- Show loss surfaces side-by-side (contour plots)
- Watch different optimisation paths converge to different optima
- For Gaussian: show MLE = OLS (they coincide!)
- For non-Gaussian: show how OLS gives "wrong" answers
- Interactive: toggle between loss functions, see how estimates differ

**Technical approach**: Extend the 2D optimisation page with multiple contour overlays or split view.

**Pedagogical point**: MLE isn't arbitrary - it's the loss function that "matches" the data-generating process.

---

## 3. Residual Diagnostics Detective

**Concept**: Interactive tool where users diagnose model problems from residual plots.

**Why it fits**: The claude-concept-chat mentions "Residual patterns detective" as a teaching approach. Also connects to "Statistics as Circuit Boards" - residuals are the "signal" showing whether the circuit is working correctly.

**Key features**:
- Present residual plots from a mystery model
- User guesses: "What's wrong?" (wrong family, missing predictor, wrong link, outliers)
- Reveal the answer, show the fix, watch diagnostics improve
- Gamified: score based on correct diagnoses
- Progressive difficulty: start with obvious patterns, increase subtlety

**Technical approach**: Pre-computed "broken" models with characteristic patterns. Could be scenario cards like the tutorials.

**Educational flow**: Builds on tutorials 3-4 (Poisson → NegBin) which already show overdispersion diagnostics.

---

## 4. The GLM "Circuit Board" Builder

**Concept**: Visual, modular representation of a GLM where users wire together components.

**Why it fits**: Direct implementation of the "Statistics as Circuit Boards" metaphor from JonStats. Also implements the three-component model from the concept chat: predictor transformers h(X), link g(μ), and noisemaker f(Y|μ).

**Key features**:
- Drag-and-drop components:
  - **Predictor transformers** (log, sqrt, polynomial) → feed into linear predictor
  - **Link function block** (identity, log, logit) → transforms η to μ
  - **Distribution block** (Gaussian, Poisson, Binomial, Gamma) → generates Y from μ
- Show data flowing through the circuit: X → h(X) → Xβ → g⁻¹(Xβ) = μ → f(Y|μ) → Y
- Mismatch warnings: "You've connected a logit link to continuous data - the circuit won't work!"
- Animate: trace a single observation through the pipeline

**Technical approach**: Canvas/SVG-based node editor, or simpler: select components from dropdowns and see the "wiring diagram" update.

**This is the "big vision" page** - ties everything together.

---

## 5. Mixed Models Extension: Random Effects Visualised

**Concept**: Extend beyond fixed-effects GLMs to show how random effects work.

**Why it fits**: Natural progression from GLMs. JonStats covers "Causal Inference" which often requires hierarchical/multilevel models. UK audiences (your target) frequently work with clustered data (schools, hospitals, regions).

**Key features**:
- Start with data that has clustering (e.g., students within schools)
- Show: what happens if we ignore clustering? (wrong SEs, overconfident inference)
- Introduce random intercepts: each group gets its own baseline
- Visualise shrinkage: group estimates "pulled toward" the grand mean
- Show the variance components: σ²_between vs σ²_within

**Technical approach**: Simpler than full GLMM - could focus just on random intercepts in a linear model, which has closed-form solutions.

**Pedagogical point**: "Fixed effects explain; random effects account for structure we can't/don't want to explain."

---

## Session Priority Suggestion

1. **Loss Functions Compared** - builds directly on optimisation work, relatively contained scope
2. **Residual Diagnostics Detective** - gamified, high engagement, uses existing tutorial data
3. **Simulation-Based Inference** - ties into JonStats simulation emphasis
4. **Circuit Board Builder** - ambitious but transformative, the "vision" piece
5. **Mixed Models** - extension work once GLM foundation is solid

---

## Technical Notes for Future Claude

- All visualisations use standalone HTML with inline CSS/JS (no build step)
- KaTeX for maths rendering (CDN)
- Plotly.js for 3D visualisations
- Canvas API for 2D custom drawings
- UK English throughout ("optimisation", "visualisation", "colour")
- Purple (#9b59b6) is the accent colour for optimisation-related content
- Tutorial pages link to optimisation section from fitting.html
- The optimization/ folder contains the progressive 1D → 2D → 3D → 4D visualisations

---

*Last updated: December 2025*
*Current state: 5 tutorials complete (Gaussian, Binomial, Poisson, NegBin, Gamma), optimisation section complete (1D-4D)*
