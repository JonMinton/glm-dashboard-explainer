# Architecture Decisions

## ADR-001: Tech Stack Selection

**Status**: ACCEPTED

**Context**: Need to choose between:
1. React + R/Plumber backend
2. Quarto + Observable JS
3. Svelte/React + WebR (in-browser R)

**Considerations**:
- User has R background (JonStats site)
- GitHub Pages hosting preferred for simplicity
- GLM fitting requires either JS library or R backend
- Interactive sliders and real-time updates are core requirements

**Decision**: **Quarto-based hybrid approach**

- **Primary framework**: Quarto site (consistent with JonStats workflow)
- **Code examples**: R and optionally Python for follow-along exercises
- **Interactive visualizations**: Observable JS, React components, or custom JS as needed
- **Hosting**: GitHub Pages (static site)

**Rationale**:
- Familiar workflow for the author
- R/Python code blocks serve pedagogical purpose (learners can copy/adapt)
- Observable JS integrates well with Quarto for interactivity
- Complex visualizations (flow diagram, sliders) may use React via Quarto's support for custom HTML/JS

---

## ADR-002: Data Strategy

**Status**: ACCEPTED

**Context**: Should datasets be simulated, real, or both?

**Options**:
1. **Simulated only** - Know true parameters, can "reveal answer"
2. **Real only** - Authentic but no ground truth
3. **Hybrid** - Simulated for guided learning, real for exploration

**Decision**: **Real open-source datasets**

Use authentic, publicly available datasets - one per scenario/GLM family. Different datasets demonstrate why different GLMs exist: each data generating process has characteristics that make a particular model family appropriate.

**Datasets by GLM family**:

| GLM Family | Data Characteristics | Candidate Datasets |
|------------|---------------------|-------------------|
| Binomial (Logistic) | Binary 0/1 outcomes | Heart disease (UCI), Titanic, diabetes prediction |
| Poisson | Counts (0, 1, 2, ...), no upper bound | Bike sharing demand, publication counts, goals scored |
| Negative Binomial | Overdispersed counts (variance > mean) | Insurance claims, species counts |
| Gamma | Positive continuous, right-skewed | Medical costs, waiting times, insurance payouts |
| Gaussian | Continuous, symmetric, unbounded | Height/weight, test scores, crop yields |
| Zero-Inflated | Counts with excess zeros | Species abundance, healthcare utilisation |

**Pedagogical rationale**: Each dataset naturally exhibits properties that make alternative models inappropriate - learners discover *why* the GLM framework exists by seeing what goes wrong with mismatched models.

**Note**: Without known "true" parameters, pedagogy shifts from "recover the truth" to "interpret what the data tells us" - which is actually more realistic.

---

## ADR-003: Page Flow Architecture

**Status**: ACCEPTED

**Decision**: Linear guided flow with gating

Each page must be interacted with before proceeding:
- Page 1: Must select scenario
- Page 2: Must interact with data table
- Page 3: Must expand model family info
- Page 4: Must try at least one transformation
- Page 5: Must either adjust sliders OR run algorithm

Navigation state encoded in URL for bookmarking/sharing.

---

## ADR-004: Component Architecture

**Status**: ACCEPTED

**Decision**: Modular, reusable components

Core components (regardless of framework):
1. **DataTable** - Paginated data display
2. **FlowDiagram** - Visual X → η → μ → Y → y flow
3. **TransformSelector** - Dropdown for h(), g(), f() choices
4. **ParameterSlider** - β and α controls with real-time updates
5. **DistributionPlot** - PDF/PMF visualization
6. **LikelihoodDisplay** - Current ℓ(β,α) value and contour plot
7. **DiagnosticsPanel** - Residual plots, Q-Q, etc.

---

## ADR-005: Mathematical Notation

**Status**: ACCEPTED

**Decision**: Consistent notation throughout

| Symbol | Meaning |
|--------|---------|
| X | Predictor matrix |
| h(X) | Transformed predictors |
| β | Systematic parameters (coefficients) |
| η | Linear predictor (Xβ) |
| g() | Link function |
| g⁻¹() | Inverse link function |
| μ | Expected value E[Y] |
| α | Dispersion/scale parameter |
| f() | Distribution family |
| Y | Random variable (model) |
| y | Observed data |

---

## ADR-006: Progressive Disclosure Levels

**Status**: ACCEPTED

**Decision**: Three-tier complexity

1. **Beginner**:
   - Hide mathematical formulas
   - Show only appropriate transforms for data type
   - Guided prompts and hints

2. **Intermediate**:
   - Show mathematical notation
   - Allow all transforms (flag inappropriate ones)
   - Less hand-holding

3. **Advanced**:
   - Full equations including likelihood, score functions
   - Access to algorithm internals (IRLS weights, etc.)
   - Loss function comparison mode
