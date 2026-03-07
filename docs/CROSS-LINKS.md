# Cross-Links: GLM Dashboard Explainer ↔ JonStats

This document maps the natural connections between the two sites so links can be added in both directions.

**GLM Dashboard**: https://jonminton.github.io/glm-dashboard-explainer/
**JonStats**: https://jonminton.github.io/JonStats/

---

## JonStats → GLM Dashboard

### (1) Intro to GLMs
`pages/main-course/intro-to-glms/index.qmd`

Suggested links:
- Where the two-part GLM framework (stochastic + systematic) is introduced, link to the **tutorial index page** which uses the same framework interactively:
  > *"Try these interactive tutorials to practice choosing the right distribution and link function for different data types: [GLM Dashboard Tutorials](https://jonminton.github.io/glm-dashboard-explainer/)"*
- Where specific GLM families are mentioned (Gaussian, Binomial, Poisson), link to the corresponding tutorial:
  - Gaussian → `tutorials/01-gaussian/systematic.html`
  - Binomial/Logistic → `tutorials/02-logistic/systematic.html`
  - Poisson → `tutorials/03-poisson/systematic.html`

### (2) Likelihood and Simulation Theory
`pages/main-course/likelihood-and-simulation-theory/index.qmd`

Suggested links:
- Where likelihood is defined and the concept of "searching for the best parameters" is introduced, link to the **optimisation visualisations**:
  > *"See these concepts in action — watch gradient ascent and Newton-Raphson navigate a likelihood surface: [Optimisation Visualised](https://jonminton.github.io/glm-dashboard-explainer/optimization/)"*
- Where log-likelihood is introduced, link to the **bridge page** (once created):
  > *"The log-likelihood surface is like a terrain that algorithms climb: [Terrain as Log-Likelihood](https://jonminton.github.io/glm-dashboard-explainer/optimization/bridge.html)"*

### (3) Complete Simulation Example
`pages/main-course/complete-simulation-example/index.qmd`

Suggested links:
- Where IRLS/MLE fitting is discussed, link to the **tutorial advanced pages** which derive log-likelihoods from scratch:
  - Gaussian LL derivation → `tutorials/01-gaussian/advanced.html`
  - Poisson LL derivation → `tutorials/03-poisson/advanced.html`

### (0) Statistics as Circuit Boards
`pages/main-course/statistics-as-circuits/index.qmd`

- The "circuit board" metaphor maps well to the GLM pipeline diagram on the dashboard index. Consider a brief mention:
  > *"For an interactive version of the GLM 'circuit', see the [GLM Dashboard](https://jonminton.github.io/glm-dashboard-explainer/)"*

---

## GLM Dashboard → JonStats

### Tutorial Index (`docs/index.html`)
Already has a footer link. Add a contextual link in the philosophy section:
> *"These tutorials are the interactive companion to [JonStats: Statistical Inference and Simulation](https://jonminton.github.io/JonStats/), which covers the theory in depth."*

### Tutorial fitting pages (`*/fitting.html`)
Where IRLS and MLE are explained conceptually, link to JonStats likelihood theory:
> *"For the mathematical foundations of likelihood and why it works, see [Likelihood and Simulation Theory](https://jonminton.github.io/JonStats/pages/main-course/likelihood-and-simulation-theory/)"*

### Tutorial advanced pages (`*/advanced.html`)
Where log-likelihoods are derived, link back to JonStats simulation:
> *"To see how these fitted models are used for inference via simulation, see [Complete Simulation Example](https://jonminton.github.io/JonStats/pages/main-course/complete-simulation-example/)"*

### Optimisation index (`docs/optimization/index.html`)
Link to JonStats likelihood theory to ground the "why":
> *"These visualisations show how MLE algorithms work in practice. For the theory behind likelihood-based inference, see [JonStats](https://jonminton.github.io/JonStats/pages/main-course/likelihood-and-simulation-theory/)"*

### Bridge page (planned: `docs/optimization/bridge.html`)
This page will explicitly connect the terrain metaphor to log-likelihood surfaces, linking heavily to both JonStats likelihood theory and the dashboard tutorials.

---

## Implementation Notes
- Keep links unobtrusive — short sentences or "See also" boxes, not banner ads
- Use consistent phrasing: "JonStats" for the theory site, "GLM Dashboard" for tutorials
- Links should be bidirectional but not circular — each link should take the reader somewhere new
