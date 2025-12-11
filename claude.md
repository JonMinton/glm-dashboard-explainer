# GLM Dashboard Explainer

An interactive pedagogical tool for teaching Generalised Linear Models (GLMs).

## Project Vision

Build a guided, step-by-step interactive dashboard that helps learners understand:
1. How different data types require different model families
2. The role of link functions in connecting linear predictors to response constraints
3. How maximum likelihood estimation "tunes" model parameters
4. The distinction between systematic (β) and random (α) components

## Core Pedagogical Framework

The GLM is presented as a data flow:

```
[X₁] ─h₁()→ ┐
[X₂] ─h₂()→ ├─→ [η = Xβ] ─g⁻¹()→ [μ] ─f(·;μ,α)→ [Y]
[X₃] ─h₃()→ ┘                              ↓
                                      [y] (observed)
```

Where:
- **h()** = Predictor transformers (log, sqrt, polynomial)
- **η = Xβ** = Linear predictor
- **g⁻¹()** = Inverse link function (logit⁻¹, exp, identity)
- **μ** = Expected value of Y
- **f()** = Distribution family (Binomial, Poisson, Gaussian, etc.)
- **Y** = Random variable (what the model says could happen)
- **y** = Observed data (what actually happened)

## Key Distinctions to Maintain

1. **Y vs y**: Y is the modelled random variable; y is observed data
2. **β vs α**: β tunes the systematic component (via Xβ → μ); α tunes dispersion in f()
3. **Link vs Distribution**: These are separate choices, though often paired conventionally

## Page Structure (Guided Flow)

1. **Scenario Selection** - Choose a data problem type (binary, count, continuous, etc.)
2. **Data Exploration** - Paginated table view of the dataset
3. **Model Family Selection** - Choose distribution and link function
4. **Predictor Transformations** - Apply h() transforms to X variables
5. **Model Fitting** - Manual slider exploration then algorithmic optimization
6. **Advanced: Loss Function Comparison** - Compare MLE to other loss functions

## Tech Stack

**Primary**: Quarto site (consistent with JonStats workflow)

- **Structure**: Quarto pages with guided navigation
- **Code examples**: R and Python for follow-along exercises
- **Interactive visualizations**: Observable JS for simpler interactions, React/custom JS for complex components (flow diagram, parameter sliders)
- **Hosting**: GitHub Pages (static site)
- **GLM fitting**: Pre-computed in R during build, or WebR for in-browser computation where needed

## Scenarios to Implement

Priority order (MVP first):
1. **Hospital Readmissions** (Binary/Logistic) - PRIMARY MVP
2. **Insurance Claims** (Count/Poisson)
3. **Equipment Lifespan** (Positive continuous/Gamma)
4. **Crop Yields** (Continuous/Gaussian)

Later expansion:
- Species Abundance (Zero-inflated)
- Market Survey (Ordinal)

## Development Principles

- **One concept per page** - Don't mix link functions and loss functions
- **Concrete before abstract** - See data before equations
- **Active before passive** - Manipulate before optimize
- **Build intuition before automation** - Manual sliders before algorithms
- **Progressive disclosure** - Beginner/Intermediate/Advanced modes

## Key Resources

- [JonStats Course Materials](https://jonminton.github.io/JonStats/)
- Prior discussion: `support/claude-concept-chat.md`

## File Structure

```
glm-dashboard-explainer/
├── claude.md                 # This file - project overview
├── _quarto.yml               # Quarto project configuration
├── .claude/
│   ├── settings.json         # Claude Code settings
│   ├── architecture.md       # Architectural decisions (ADRs)
│   ├── components.md         # Component specifications
│   └── commands/             # Custom slash commands
│       ├── context.md        # Load full project context
│       ├── review-page.md    # Review page implementation
│       ├── add-scenario.md   # Add new scenario
│       └── check-notation.md # Check notation consistency
├── support/
│   └── claude-concept-chat.md  # Prior discussion context
├── pages/                    # Quarto pages (the actual content)
│   ├── index.qmd             # Landing / scenario selection
│   ├── data.qmd              # Data exploration page
│   ├── model.qmd             # Model builder page
│   ├── transform.qmd         # Predictor transformations
│   ├── fit.qmd               # Fitting page
│   └── advanced/             # Advanced topics
│       └── loss-functions.qmd
├── components/               # Reusable JS/Observable components
├── data/                     # Sample datasets (R/CSV)
├── R/                        # R scripts for data generation, examples
└── _site/                    # Built site (git-ignored)
```
