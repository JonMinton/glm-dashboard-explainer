# Cross-Links: GLM Dashboard Explainer ↔ JonStats

This document maps the natural connections between the two sites so links can be added in both directions.

**GLM Dashboard**: https://stats-board.jonminton.net/
**JonStats**: https://jonminton.github.io/JonStats/

---

## JonStats → GLM Dashboard

### (1) Intro to GLMs
`pages/main-course/intro-to-glms/index.qmd`

Suggested links:
- Where the two-part GLM framework (stochastic + systematic) is introduced, link to the **tutorial index page** which uses the same framework interactively:
  > *"Try these interactive tutorials to practice choosing the right distribution and link function for different data types: [GLM Dashboard Tutorials](https://stats-board.jonminton.net/)"*
- Where specific GLM families are mentioned (Gaussian, Binomial, Poisson), link to the corresponding tutorial:
  - Gaussian → `tutorials/01-gaussian/systematic.html`
  - Binomial/Logistic → `tutorials/02-logistic/systematic.html`
  - Poisson → `tutorials/03-poisson/systematic.html`

### (2) Likelihood and Simulation Theory
`pages/main-course/likelihood-and-simulation-theory/index.qmd`

Suggested links:
- Where likelihood is defined and the concept of "searching for the best parameters" is introduced, link to the **optimisation visualisations**:
  > *"See these concepts in action — watch gradient ascent and Newton-Raphson navigate a likelihood surface: [Optimisation Visualised](https://stats-board.jonminton.net/optimization/)"*
- Where log-likelihood is introduced, link to the **bridge page** (once created):
  > *"The log-likelihood surface is like a terrain that algorithms climb: [Terrain as Log-Likelihood](https://stats-board.jonminton.net/optimization/bridge.html)"*

### (3) Complete Simulation Example
`pages/main-course/complete-simulation-example/index.qmd`

Suggested links:
- Where IRLS/MLE fitting is discussed, link to the **tutorial advanced pages** which derive log-likelihoods from scratch:
  - Gaussian LL derivation → `tutorials/01-gaussian/advanced.html`
  - Poisson LL derivation → `tutorials/03-poisson/advanced.html`

### (2b) Likelihood and Simulation Theory → Inference section (PLANNED, not yet added to JonStats)
Where the King (1998) variance formula and `optim(..., hessian = TRUE)` are introduced, link to the interactive versions:
> *"Probe the curvature of a likelihood surface yourself, and watch the Hessian become a confidence ellipse: [Standard Errors from Curvature](https://stats-board.jonminton.net/inference/curvature.html)"*

Where the "barefoot and blind" metaphor appears:
> *"An interactive version of this exact exercise — three probes filling in the Hessian matrix — is on the [GLM Dashboard](https://stats-board.jonminton.net/inference/curvature.html)"*

### (3b) Complete Simulation Example → Inference section (PLANNED, not yet added to JonStats)
Where the marble-vs-jumping-bean contrast is introduced:
> *"See the two portraits side by side — Hessian ellipse vs Metropolis walker, with Wald and credible intervals compared numerically: [Beyond the Quadratic: Bayesian Uncertainty](https://stats-board.jonminton.net/inference/bayes.html)"*

### (0) Statistics as Circuit Boards
`pages/main-course/statistics-as-circuits/index.qmd`

- The "circuit board" metaphor maps well to the GLM pipeline diagram on the dashboard index. Consider a brief mention:
  > *"For an interactive version of the GLM 'circuit', see the [GLM Dashboard](https://stats-board.jonminton.net/)"*

---

## GLM Dashboard → JonStats / blog (IMPLEMENTED)

All links below are now live in the dashboard pages. Convention: plain `<a href>` links (no `target="_blank"` — matching the site's existing convention), small caption text or each page's own info/insight box class.

### Tutorial Index (`docs/index.html`)
- Philosophy section: companion-site link to [JonStats](https://jonminton.github.io/JonStats/) *(pre-existing)*
- Above the tutorial cards: "New to GLMs? Start with the theory in [Introduction to Generalised Linear Models](https://jonminton.github.io/JonStats/pages/main-course/intro-to-glms/) on JonStats."
- Below the tutorial cards: "Tutorials 4–8 extend the framework beyond the original blog series — see the [25-part GLM series](https://jonminton.github.io/jon-blog/glms.html) that started it all."
- Optimisation section: [Likelihood and Simulation Theory](https://jonminton.github.io/JonStats/pages/main-course/likelihood-and-simulation-theory/) *(pre-existing)*
- Footer: JonStats home *(pre-existing)*

### Tutorial fitting pages (all eight `*/fitting.html`)
One-line further-reading note just before the nav buttons (small caption `<p>` in tutorials 1–3; `insight-box` in tutorials 4–8):
> *"Why does maximising the likelihood work? See [Likelihood and Simulation Theory](https://jonminton.github.io/JonStats/pages/main-course/likelihood-and-simulation-theory/) on JonStats."*

### Tutorial advanced pages
- `01-gaussian/advanced.html` and `03-poisson/advanced.html` (end-of-page takeaways): "To use a fitted model for simulation-based inference, see the [Complete Simulation Example](https://jonminton.github.io/JonStats/pages/main-course/complete-simulation-example/) on JonStats." *(JonStats links back to these exact pages, completing the loop.)*
- `02-logistic/advanced.html` (after Key Takeaways): "Compare with the blog derivation: [Part Ten — Log Likelihood estimation for Logistic Regression](https://jonminton.github.io/jon-blog/posts/glms/likelihood-and-simulation-theory/lms-are-glms-part-10/)."

### Tutorial code pages
- `02-logistic/code.html` (next-steps box, odds-ratio interpretation): "Don't stargaze at coefficients — see how to interpret GLM outputs properly in [Intro to GLMs](https://jonminton.github.io/JonStats/pages/main-course/intro-to-glms/)."

### Tutorials 6–8 systematic pages (beyond JonStats coverage)
Framing line in each context panel: "This tutorial extends the GLM framework from the [JonStats](https://jonminton.github.io/JonStats/) course to [bounded proportions / ordered categories / zero-inflated counts] — material not covered in the original series."

### Optimisation index (`docs/optimization/index.html`)
End of explanation panel: "For the theory behind these surfaces — likelihood, `optim()` and Fisher information — see [Likelihood and Simulation Theory](https://jonminton.github.io/JonStats/pages/main-course/likelihood-and-simulation-theory/) on JonStats."

### Bridge page (`docs/optimization/bridge.html`)
- Theory see-also box: [Likelihood and Simulation Theory](https://jonminton.github.io/JonStats/pages/main-course/likelihood-and-simulation-theory/) *(pre-existing)*, plus "Blog origin of the landscape metaphor: [Part Five — Traversing the Likelihood Landscape](https://jonminton.github.io/jon-blog/posts/glms/likelihood-and-simulation-theory/lms-are-glms-part-05/)."
- Footer: JonStats home *(pre-existing)*

### MCMC page (`docs/optimization/mcmc.html`)
Further-reading note at the end of "The Bayesian Perspective" card: the marble-vs-jumping-bean analogy in [Statistical Simulation: A Complete Example](https://jonminton.github.io/JonStats/pages/main-course/complete-simulation-example/) on JonStats, and the blog version, [Part Thirteen — On Marbles and Jumping Beans](https://jonminton.github.io/jon-blog/posts/glms/complete-simulation-example/lms-are-glms-part-13/).

### Inference section (`docs/inference/`, added 2026-07)
- `index.html` (crosslink box): [Likelihood and Simulation Theory](https://jonminton.github.io/JonStats/pages/main-course/likelihood-and-simulation-theory/) — "the same argument in R code", citing the barefoot-and-blind summit metaphor.
- `curvature.html` (crosslink box): Likelihood and Simulation Theory (the `optim(hessian = TRUE)` → `solve(-hessian)` → `mvrnorm()` pipeline) and the [Complete Simulation Example](https://jonminton.github.io/JonStats/pages/main-course/complete-simulation-example/) (`coefficients()`/`vcov()`/`sigma()` applied end-to-end).
- `bayes.html` (crosslink box): Complete Simulation Example — noting it tells the frequentist-vs-Bayesian contrast "in valley form" (marble vs jumping bean; the dashboard keeps its peak/walker framing).

### Tutorial code pages (all eight, added 2026-07)
Cross-link before the nav buttons (list item in tutorials 1–2, teal box in 3–8):
> *"Where do the `Std. Error` columns in these outputs come from? See [Standard Errors from Curvature](../../inference/curvature.html)"*

### Inference testing trio + fork structure (added 2026-07-17)
- The inference section is now explicitly **branch-shaped**: `index.html`'s route cards present
  the curvature route (purple: curvature → wald → lr-test → model-comparison) and the sampling
  route (teal: bayes) as parallel traditions; `curvature.html` ends with dual fork buttons
  ("Continue this route: Wald tests" / "The other route: Bayesian uncertainty"); nav bars on all
  six pages colour-code branch membership.
- `wald.html` → JonStats [P-Values and Statistical Significance](https://jonminton.github.io/JonStats/pages/extra-courses/p-values-stat-sig/)
  (interpretation battles; the page covers only where the number comes from).
- `model-comparison.html` → Tutorial 4's distribution page (AIC used in anger for Poisson vs
  NegBin); one-sentence teal nods on wald (credible intervals) and model-comparison (Bayes
  factors/LOO) point across the fork.

### Optimisation → Inference internal links (added 2026-07)
- All optimisation nav bars now end with an **Uncertainty** item → `../inference/index.html` (and 2d/3d/4d regained the missing MCMC nav item).
- `2d.html`: foreshadowing line — the steepness of the surface "turns out to be the standard error".
- `multi-optima.html` (representativeness boxes): Hessian-ellipse box → `inference/curvature.html`; MCMC box → `inference/bayes.html`.
- `mcmc.html` (Bayesian Perspective card): "visit-maps into numbers" → `inference/bayes.html`.
- `bridge.html` (after concept table): the information/ellipse/standard-error rows → `inference/index.html`.

---

## Implementation Notes
- Keep links unobtrusive — short sentences or "See also" boxes, not banner ads
- Use consistent phrasing: "JonStats" for the theory site, "GLM Dashboard" for tutorials
- Links should be bidirectional but not circular — each link should take the reader somewhere new
