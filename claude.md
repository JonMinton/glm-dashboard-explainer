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

## Tutorial Series (Current Focus)

A series of guided tutorials, each demonstrating a complete GLM workflow for different data types.
See `.claude/specs/tutorial-series.md` for detailed implementation plan.

### Current Status

| # | Tutorial | GLM Family | Status |
|---|----------|------------|--------|
| 1 | Heart Rate Prediction | Gaussian + Identity | **COMPLETE** |
| 2 | Heart Disease Classification | Binomial + Logit | **COMPLETE** |
| 3 | Bike Rental Counts | Poisson + Log | **COMPLETE** |
| 4 | Overdispersed Counts | Negative Binomial + Log | **COMPLETE** |
| 5 | Blood Pressure Prediction | Gamma + Log | **COMPLETE** |

### Tutorial Files
```
docs/
├── index.html                      # Tutorial/datasets index page
└── tutorials/
    ├── 01-gaussian/                # Tutorial 1: Heart Rate (Gaussian)
    │   ├── systematic.html         # Select response & predictors
    │   ├── link.html               # Link function selection
    │   ├── distribution.html       # Distribution selection
    │   ├── fitting.html            # Fitting method explanation
    │   ├── code.html               # R/Python implementation
    │   └── advanced.html           # Log-likelihood derivation (KaTeX)
    ├── 02-logistic/                # Tutorial 2: Heart Disease (Binomial)
    ├── 03-poisson/                 # Tutorial 3: Bike Rentals (Poisson)
    ├── 04-negbin/                  # Tutorial 4: Overdispersed Counts
    └── 05-gamma/                   # Tutorial 5: Blood Pressure (Gamma)
```

### Design Pattern
Each tutorial follows a 6-page flow:
1. **Systematic** → Select response & predictors
2. **Link** → Choose link function (with wrong-choice feedback)
3. **Distribution** → Choose distribution family
4. **Fitting** → Understand MLE/IRLS
5. **Code** → R and Python implementation
6. **Advanced** → Log-likelihood derivation, custom MLE

### Key Technical Decisions
- **KaTeX** for LaTeX math rendering (CDN-based)
- **Standalone HTML** prototypes (no Quarto yet)
- **Tabbed R/Python** code panels
- **Validated outputs** against actual R/Python sessions

## Development Principles

- **One concept per page** - Don't mix link functions and loss functions
- **Concrete before abstract** - See data before equations
- **Active before passive** - Manipulate before optimize
- **Build intuition before automation** - Manual sliders before algorithms
- **Progressive disclosure** - Beginner/Intermediate/Advanced modes

## Key Resources

- [JonStats Course Materials](https://jonminton.github.io/JonStats/)
- Prior discussion: `support/claude-concept-chat.md`

## User Feedback System

The tutorials are in alpha testing. Users can report bugs and request features via GitHub Issues.

### Querying Feedback (for Claude sessions)

```bash
# List all bug reports
gh issue list --label bug

# List all feature requests
gh issue list --label enhancement

# View a specific issue
gh issue view <issue-number>

# List open issues with details
gh issue list --label bug --state open --json number,title,body
```

### Feedback Infrastructure

- **Issue templates**: `.github/ISSUE_TEMPLATE/` (bug_report.md, feature_request.md)
- **Feedback widget**: `docs/js/feedback.js` - floating "?" button on all pages
- **Auto-context**: Widget pre-fills issues with current tutorial/page location

### Adding Feedback to New Pages

Run the build script to add the feedback widget to any new HTML files:
```bash
python3 scripts/build/add-feedback-widget.py
```

## File Structure

```
glm-dashboard-explainer/
├── CLAUDE.md                 # This file - project overview
├── _quarto.yml               # Quarto project configuration
├── .github/
│   └── ISSUE_TEMPLATE/       # GitHub issue templates
│       ├── bug_report.md
│       ├── feature_request.md
│       └── config.yml
├── .claude/
│   ├── settings.json         # Claude Code settings
│   ├── handover/             # Session handover documents
│   ├── architecture.md       # Architectural decisions (ADRs)
│   └── commands/             # Custom slash commands
├── docs/                     # Main tutorial site (GitHub Pages source)
│   ├── index.html            # Tutorial index page
│   ├── js/
│   │   └── feedback.js       # Feedback widget (runtime JS)
│   ├── css/                  # Shared CSS (for future use)
│   └── tutorials/
│       ├── 01-gaussian/      # 6 HTML files per tutorial
│       ├── 02-logistic/
│       ├── 03-poisson/
│       ├── 04-negbin/
│       └── 05-gamma/
├── scripts/
│   ├── build/                # Site processing scripts (Python)
│   │   ├── extract-css.py
│   │   └── add-feedback-widget.py
│   ├── R/                    # R validation scripts
│   │   └── validate-*.R
│   └── py/                   # Python validation scripts
│       └── validate_*.py
├── data/                     # Sample datasets (JSON)
│   └── heart.json
└── _site/                    # Quarto build output (git-ignored)
```
