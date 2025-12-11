# Tutorial Series Plan: GLM Family Case Studies

## Overview

A series of 4-5 guided tutorials, each walking through a complete GLM workflow for a different data type and distribution family. All tutorials share a common design pattern and 6-page structure.

---

## Current Status

| Tutorial | GLM Family | Status | Pages Complete |
|----------|------------|--------|----------------|
| 1. Heart Rate (Gaussian) | Gaussian + Identity | **COMPLETE** | 6/6 + Advanced |
| 2. Heart Disease (Logistic) | Binomial + Logit | NOT STARTED | 0/6 |
| 3. Count Data (Poisson) | Poisson + Log | NOT STARTED | 0/6 |
| 4. Overdispersed Counts (NegBin) | Negative Binomial + Log | NOT STARTED | 0/6 |
| 5. Positive Continuous (Gamma) | Gamma + Log/Inverse | OPTIONAL | 0/6 |

---

## Common 6-Page Structure (Template)

Each tutorial follows this flow:

```
Page 1: Systematic Component (tutorial-{id}.html)
  └─→ Drag & drop: Select response + predictors
  └─→ Output: η = β₀ + β₁X₁ + β₂X₂ + ...

Page 2: Link Function (tutorial-{id}-link.html)
  └─→ Card selection: Choose appropriate link
  └─→ Dialogs: Explain why each choice is right/wrong for this data

Page 3: Distribution (tutorial-{id}-distribution.html)
  └─→ Card selection: Choose distribution family
  └─→ Interactive: Show PDF/PMF characteristics

Page 4: Fitting Method (tutorial-{id}-fitting.html)
  └─→ Explain: MLE / IRLS / OLS equivalence where applicable
  └─→ Interactive: Optional manual slider exploration

Page 5: Implementation (tutorial-{id}-code.html)
  └─→ Tabbed: R and Python code examples
  └─→ Output: Validated results from actual sessions

Page 6: Advanced (tutorial-{id}-advanced.html)
  └─→ Log-likelihood derivation with KaTeX
  └─→ Custom MLE implementation (optim / scipy.optimize)
  └─→ Score equations and matrix notation
```

---

## Tutorial 1: Gaussian GLM (COMPLETE)

**Decision Problem**: Predict maximum heart rate from patient characteristics
**Dataset**: UCI Heart Disease (Cleveland subset, n=303)
**Outcome**: `thalach` (continuous, ~60-200 bpm)
**Predictors**: `age`, `exang` (binary), `oldpeak` (continuous)

### Files (all in `/prototype/`)
- [x] `tutorial.html` - Systematic component (drag & drop)
- [x] `tutorial-link.html` - Link function selection (identity)
- [x] `tutorial-distribution.html` - Distribution selection (Gaussian)
- [x] `tutorial-fitting.html` - Fitting method (MLE/IRLS)
- [x] `tutorial-code.html` - R/Python implementation
- [x] `tutorial-advanced.html` - Log-likelihood derivation, custom MLE

### Key Learning Points
- OLS is MLE for Gaussian GLM
- Identity link: coefficients are additive effects (bpm change per unit)
- Normal equations: β = (X'X)⁻¹X'y

### Validated Outputs
```
Coefficients:
  Intercept: 203.37
  age:       -0.83
  exang:    -14.25
  oldpeak:   -3.78

Dispersion (σ²): 366.98
AIC: 2655.2
```

---

## Tutorial 2: Logistic Regression (PLANNED)

**Decision Problem**: Predict whether a patient has heart disease (yes/no)
**Dataset**: UCI Heart Disease (same dataset, different outcome)
**Outcome**: `target` (binary, 0=no disease, 1=disease)
**Predictors**: `age`, `sex`, `cp` (chest pain type), `thalach`, `oldpeak`

### Why This Tutorial
- **Same dataset** as Tutorial 1 → learners see how GLM framework adapts
- Binary outcomes are extremely common in practice
- Natural progression from continuous → binary
- Introduces odds ratios and probability interpretation

### Key Learning Points
- Logit link bounds predictions to (0,1)
- Coefficients are log-odds ratios
- No closed-form solution → iterative fitting required
- Deviance and pseudo-R² for binary outcomes

### Link Function Page: Logit vs Probit vs Others

The link function selection page should present **4 options** with educational feedback:

| Link | Correct? | Dialog Type |
|------|----------|-------------|
| **Logit** | ✓ Correct | Success - explain odds ratio interpretation |
| **Probit** | ~ Semi-valid | Warning - historically important, explain context |
| **Identity** | ✗ Wrong | Error - predictions not bounded to (0,1) |
| **Log** | ✗ Wrong | Error - doesn't map to probability scale properly |

#### Probit Dialog Content (Semi-valid)
The probit link should be presented as a **historically important alternative** with this educational content:

**Title**: "A Valid Historical Choice..."

**Key points to cover**:
1. **What probit does**: Uses the inverse standard normal CDF (Φ⁻¹) instead of log-odds
2. **Historical popularity**:
   - Dominated before ~1980s, especially in economics and bioassay
   - Arose from "latent variable" interpretation: assume underlying continuous variable, threshold determines binary outcome
   - Easier to compute by hand using normal distribution tables
3. **Why logit won**:
   - Odds ratio interpretation is more intuitive for practitioners
   - Log-odds have a cleaner algebraic form
   - With modern computation, "ease of calculation" no longer matters
   - Results are nearly identical in practice (curves are very similar in the middle)
4. **When probit is still used**:
   - Economics (tradition, latent variable story)
   - Dose-response studies (bioassay heritage)
   - When you genuinely believe in a latent normal threshold mechanism
5. **Practical note**: Coefficients are NOT directly comparable between logit and probit (different scales)

**Dialog conclusion**: "For this tutorial, we'll use the logit link - it's the modern default and gives easily interpretable odds ratios. But probit would give very similar predictions!"

#### Identity Link Dialog (Wrong)
Explain that:
- Identity link allows predictions outside (0,1)
- A model predicting P(disease) = 1.3 or P(disease) = -0.2 makes no sense
- This is the "linear probability model" - sometimes used but has fundamental problems

#### Log Link Dialog (Wrong)
Explain that:
- Log link ensures predictions > 0, but doesn't bound them below 1
- Would allow P(disease) = 5, which is nonsensical
- Log link is for counts (Poisson), not probabilities

### Files to Create
- [ ] `tutorial-logistic.html` - Systematic component
- [ ] `tutorial-logistic-link.html` - Link function (logit, with probit as semi-valid)
- [ ] `tutorial-logistic-distribution.html` - Distribution (Binomial)
- [ ] `tutorial-logistic-fitting.html` - Fitting (IRLS)
- [ ] `tutorial-logistic-code.html` - R/Python glm(..., family=binomial())
- [ ] `tutorial-logistic-advanced.html` - Binomial log-likelihood derivation

### Expected Outputs
```r
glm(target ~ age + sex + cp + thalach + oldpeak,
    family = binomial(link = "logit"), data = heart)
```

### Probit Comparison (for advanced section or code page)
```r
# Compare logit vs probit
logit_fit <- glm(target ~ age + sex + cp + thalach + oldpeak,
                 family = binomial(link = "logit"), data = heart)
probit_fit <- glm(target ~ age + sex + cp + thalach + oldpeak,
                  family = binomial(link = "probit"), data = heart)

# Coefficients are on different scales but predictions nearly identical
# Rule of thumb: probit coefficients ≈ logit coefficients × 0.625
```

---

## Tutorial 3: Poisson Regression (PLANNED)

**Decision Problem**: Predict count of bike rentals given weather/day conditions
**Dataset**: UCI Bike Sharing Dataset (daily aggregates)
**Outcome**: `cnt` (count, 0-8000+ rentals per day)
**Predictors**: `temp`, `hum`, `windspeed`, `workingday`, `weathersit`

### Alternative Datasets
- Hospital ER admissions by day
- Publication counts by researcher
- Goals scored in football matches
- Insurance claim counts

### Why This Tutorial
- Introduces count data (non-negative integers)
- Log link ensures positive predictions
- Rate ratios interpretation (multiplicative effects)
- Exposure/offset concept (optional)

### Key Learning Points
- Counts can't be negative → need appropriate distribution
- Log link: exp(β) = rate ratio
- Mean = Variance assumption (Poisson)
- Residual deviance / Pearson χ² for checking fit

### Files to Create
- [ ] `tutorial-poisson.html` - Systematic component
- [ ] `tutorial-poisson-link.html` - Link function (log)
- [ ] `tutorial-poisson-distribution.html` - Distribution (Poisson)
- [ ] `tutorial-poisson-fitting.html` - Fitting (MLE/IRLS)
- [ ] `tutorial-poisson-code.html` - R/Python glm(..., family=poisson())
- [ ] `tutorial-poisson-advanced.html` - Poisson log-likelihood derivation

---

## Tutorial 4: Negative Binomial (PLANNED)

**Decision Problem**: Same as Tutorial 3, but demonstrating overdispersion
**Dataset**: Same Bike Sharing data (or insurance claims)
**Outcome**: Same count variable

### Why This Tutorial
- Natural follow-on from Poisson
- Demonstrates overdispersion diagnostic
- Shows what happens when Poisson assumptions fail
- Introduces dispersion parameter

### Key Learning Points
- Overdispersion: Variance > Mean
- Poisson underestimates uncertainty when overdispersed
- NegBin adds dispersion parameter θ
- Model comparison (AIC, likelihood ratio)

### Pedagogical Approach
1. Fit Poisson model to same data as Tutorial 3
2. Show diagnostic: residual deviance >> df
3. Fit NegBin, compare
4. Discuss when to choose which

### Files to Create
- [ ] `tutorial-negbin.html` - Systematic component
- [ ] `tutorial-negbin-link.html` - Link function (log)
- [ ] `tutorial-negbin-distribution.html` - Distribution (NegBin)
- [ ] `tutorial-negbin-fitting.html` - Fitting (MLE)
- [ ] `tutorial-negbin-code.html` - R MASS::glm.nb() / Python statsmodels
- [ ] `tutorial-negbin-advanced.html` - NegBin log-likelihood derivation

---

## Tutorial 5: Gamma GLM (OPTIONAL)

**Decision Problem**: Predict insurance claim amount (given a claim occurred)
**Dataset**: Insurance claims dataset
**Outcome**: Claim amount in currency (positive, right-skewed)
**Predictors**: Age, policy type, vehicle age, etc.

### Why This Tutorial
- Positive continuous data (not counts, not symmetric)
- Right-skewed distributions common in finance/insurance
- Introduces inverse link (canonical) vs log link (common)
- Completes the "family" of common GLMs

### Key Learning Points
- Gamma for positive continuous data
- Log link often preferred over inverse for interpretability
- Coefficient of variation constant (Gamma property)
- Two-part models: P(claim) × E[amount|claim]

---

## Additional Link Functions Reference

| Link | Formula | Inverse | Primary Use |
|------|---------|---------|-------------|
| Identity | g(μ) = μ | μ = η | Gaussian (continuous) |
| Log | g(μ) = ln(μ) | μ = exp(η) | Poisson, NegBin, Gamma |
| Logit | g(μ) = ln(μ/(1-μ)) | μ = 1/(1+exp(-η)) | Binomial (binary) - modern default |
| Probit | g(μ) = Φ⁻¹(μ) | μ = Φ(η) | Binomial (historical, economics) |
| Cloglog | g(μ) = ln(-ln(1-μ)) | μ = 1-exp(-exp(η)) | Binomial (asymmetric/rare events) |
| Inverse | g(μ) = 1/μ | μ = 1/η | Gamma (canonical) |
| Sqrt | g(μ) = √μ | μ = η² | Poisson (variance stabilising) |

### Logit vs Probit: Historical Context

**Pre-1980s**: Probit dominated, especially in:
- Bioassay (dose-response curves)
- Economics (discrete choice models)
- Any field with "latent variable" interpretation

**Why probit was popular**:
- Normal distribution tables were widely available
- Latent variable story: "There's an underlying continuous variable; if it crosses a threshold, we observe Y=1"
- Fitted naturally with existing statistical infrastructure

**Why logit became dominant**:
- **Odds ratios**: exp(β) has a direct interpretation as odds ratio
- **Algebraic simplicity**: Log-odds is cleaner than Φ⁻¹
- **Modern computation**: No advantage to using normal tables anymore
- **Medical/epidemiological tradition**: Odds ratios became standard

**Practical equivalence**:
- Logit and probit give nearly identical predictions in the middle range
- Differences only at extreme probabilities (tails)
- Rule of thumb: β_probit ≈ β_logit × 0.625 (or β_logit ≈ β_probit × 1.6)

**When to still use probit**:
- Economics papers (disciplinary convention)
- When you genuinely believe in latent normal mechanism
- Dose-response studies (bioassay tradition)

---

## Shared Components (To Extract)

When building multiple tutorials, extract these reusable pieces:

### CSS
- Common styling (cards, dialogs, navigation, progress indicators)
- KaTeX integration
- Code syntax highlighting

### JavaScript
- Tab switching (R/Python code panels)
- Dialog open/close logic
- Drag & drop functionality
- Card selection with feedback

### HTML Patterns
- Progress indicator (5-step dots)
- Context panel ("Your model so far")
- Navigation buttons (Back / Continue)
- Code panel structure

### Possible Template System
```
/prototype/
├── _base.html          # Common HTML structure
├── _styles.css         # Shared CSS
├── _scripts.js         # Shared JavaScript
├── templates/
│   ├── systematic.html # Template for page 1
│   ├── link.html       # Template for page 2
│   ├── distribution.html
│   ├── fitting.html
│   ├── code.html
│   └── advanced.html
└── tutorials/
    ├── gaussian/       # Tutorial 1 (current)
    ├── logistic/       # Tutorial 2
    ├── poisson/        # Tutorial 3
    ├── negbin/         # Tutorial 4
    └── gamma/          # Tutorial 5 (optional)
```

---

## Implementation Priority

1. **Tutorial 2 (Logistic)** - High value, same dataset, clear contrast with Tutorial 1
2. **Tutorial 3 (Poisson)** - Introduces count data, new dataset
3. **Tutorial 4 (NegBin)** - Natural extension of Tutorial 3
4. **Tutorial 5 (Gamma)** - Optional, lower priority

---

## Progress Tracking

### Next Steps
1. [ ] Extract common CSS/JS from Tutorial 1 into shared files
2. [ ] Create Tutorial 2 (Logistic) starting with systematic component
3. [ ] Update index page with links to both tutorials
4. [ ] Validate all code outputs against actual R/Python sessions

### Notes
- Keep KaTeX CDN approach for math rendering (working well)
- Maintain consistent navigation structure
- Test responsive design across tutorials

---

## CRITICAL: Output Validation Requirement

**ALWAYS validate regression model outputs against actual R and Python sessions before including in tutorials.**

### Validation Process
1. Write R code and run in actual R session to get real outputs
2. Write Python code and run in actual Python session to get real outputs
3. Compare coefficients, standard errors, and fit statistics between implementations
4. Only include validated outputs in tutorial HTML files
5. Document any discrepancies (e.g., MLE vs unbiased variance estimator, dispersion parameter differences)

### Why This Matters
- Illustrative/placeholder outputs can contain mathematical errors
- Real outputs ensure tutorial accuracy and build trust with learners
- Learners may run the code themselves and compare results
- Small errors in coefficients/SEs undermine the educational value

### What to Validate
- All coefficient estimates (β values)
- Standard errors
- Fit statistics (AIC, deviance, log-likelihood)
- Dispersion/scale parameters
- Degrees of freedom

### Example Validation (from Tutorial 1)
```
Validated against actual R/Python sessions:
  Intercept: 203.37 (not 200.00 placeholder)
  age:       -0.83  (not -1.00 placeholder)
  exang:    -14.25
  oldpeak:   -3.78
  Dispersion: 366.98
  AIC: 2655.2
```

---

## CRITICAL: Coefficient Consistency Across Pages

**ALL pages within a single tutorial MUST use IDENTICAL coefficient values.**

### Why This Matters
- Learners may notice if page 3 says "β₁ = -0.8" but page 5 says "β₁ = -0.83"
- Inconsistency undermines trust and causes confusion
- Rounded vs precise values must be intentional and consistent

### Canonical Coefficients by Tutorial

Define these BEFORE building any pages. Use EXACTLY these values everywhere.

#### Tutorial 1: Gaussian (Heart Rate)
```
Model: thalach ~ age + exang + oldpeak
Family: gaussian(link = "identity")

CANONICAL VALUES (use these everywhere):
  β₀ (Intercept): 203.37  (or 203.3660 when showing full precision)
  β₁ (age):       -0.83   (or -0.8298)
  β₂ (exang):    -14.25   (or -14.2542)
  β₃ (oldpeak):   -3.78   (or -3.7805)

  Dispersion (σ²): 366.98
  AIC: 2655.2
  Log-likelihood: -1322.6

INTERPRETATION TEXT (use consistently):
  - "Age: ~0.8 bpm decrease per year" (matches -0.83)
  - "Exercise angina: ~14 bpm decrease" (matches -14.25)
  - "ST depression: ~4 bpm decrease per unit" (matches -3.78)
```

#### Tutorial 2: Logistic (Heart Disease)
```
Model: target ~ age + sex + cp + thalach + oldpeak
Family: binomial(link = "logit")

CANONICAL VALUES: [TO BE VALIDATED BEFORE BUILDING]
  β₀ (Intercept): TBD
  β₁ (age):       TBD
  β₂ (sex):       TBD
  β₃ (cp):        TBD
  β₄ (thalach):   TBD
  β₅ (oldpeak):   TBD

  AIC: TBD
  Null deviance: TBD
  Residual deviance: TBD
```

### Consistency Checklist (run before committing)

For each tutorial, verify these locations use identical values:
- [ ] Context panel ("Your model so far") on each page
- [ ] Code output examples (R and Python)
- [ ] Advanced page derivations
- [ ] Interpretation text ("age decreases heart rate by X bpm")
- [ ] Any equations showing specific coefficient values
