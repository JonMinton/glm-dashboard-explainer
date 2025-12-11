# Handover: Tutorial 5 - Gamma Regression (Optional)

## Task Summary
Build the complete 6-page tutorial for positive continuous data (Gamma GLM) following the established pattern from Tutorials 1-4. This tutorial covers insurance claim amounts - data that is strictly positive and right-skewed.

## Location
Create files in: `prototype/tutorials/05-gamma/`

## Files to Create
1. `systematic.html` - Select response (claim amount) & predictors
2. `link.html` - Choose link function (log correct for multiplicative effects)
3. `distribution.html` - Choose distribution (Gamma correct, Gaussian wrong)
4. `fitting.html` - Explain IRLS fitting for Gamma
5. `code.html` - R and Python implementation with validated outputs
6. `advanced.html` - Gamma log-likelihood derivation with KaTeX

## Key Context

### Dataset
- **Source**: Need to identify a suitable insurance claims dataset
- **Options**:
  1. `MASS::Insurance` (R) - Belgian car insurance claims
  2. `CASdatasets` package - various actuarial datasets
  3. Synthetic data if no suitable public dataset
- **Outcome**: Claim amount (strictly positive continuous)
- **Predictors**: Age group, car type, region, etc.

### The Pedagogical Story
Gamma regression is for **positive continuous** outcomes that are often right-skewed:
1. Why Gaussian fails (can predict negative claim amounts)
2. How Gamma handles positive-only data with right skew
3. The multiplicative interpretation (log link gives percentage effects)
4. Variance proportional to mean squared: Var = μ²/shape

### Design Pattern
Copy structure from `prototype/tutorials/04-negbin/` but adapt content for:
- Gamma distribution (not Negative Binomial)
- Shape parameter (instead of theta)
- Positive continuous outcomes (not counts)
- Variance = μ²/shape (not μ + μ²/θ)

### Link Function Page - Options
Must include **4 options** with educational feedback:

| Link | Correct? | Dialog |
|------|----------|--------|
| **Log** | Correct | Ensures positive predictions, multiplicative interpretation |
| **Inverse** | Semi-valid | Canonical link for Gamma, but less interpretable |
| **Identity** | Wrong | Can predict negative values |
| **Logit** | Wrong | For probabilities, not positive continuous |

Note: Log is not the canonical link for Gamma (inverse is), but log is more commonly used in practice for interpretability.

### Distribution Page - Options

| Distribution | Correct? | Dialog |
|--------------|----------|--------|
| **Gamma** | Correct | Var ∝ μ², positive support, right-skewed |
| **Gaussian** | Wrong | Can predict negative values, symmetric |
| **Inverse Gaussian** | Semi-valid | Alternative for positive data, heavier tails |
| **Log-Normal** | Semi-valid | Common alternative, but not a GLM |

### Key Learning Points
1. Positive continuous data needs appropriate distribution
2. Gamma has Variance = μ²/shape (variance increases with mean)
3. Log link gives multiplicative/percentage effects
4. Shape parameter controls the spread (like precision)
5. Compare to log-transforming Y and using Gaussian

## CRITICAL: Output Validation

**DO NOT use placeholder outputs.** Before including any regression results:

1. Find/create suitable insurance claims dataset
2. Run actual R code with glm(..., family=Gamma(link="log"))
3. Run actual Python code with statsmodels Gamma
4. Record canonical values in this file before building pages

### R Validation Code
```r
# Option 1: MASS::Insurance dataset
library(MASS)
data(Insurance)
head(Insurance)

# Claims is count, but we can use it as example structure
# May need different dataset for claim AMOUNTS

# If using MASS::Insurance (Claims variable)
# Note: This is actually counts, not amounts - need better data

# Better option: Use claims per policy as quasi-continuous
Insurance$ClaimRate <- Insurance$Claims / Insurance$Holders

fit_gamma <- glm(ClaimRate ~ District + Group + Age,
                 data = Insurance,
                 family = Gamma(link = "log"),
                 subset = ClaimRate > 0)  # Gamma needs positive values
summary(fit_gamma)

# Shape parameter
MASS::gamma.dispersion(fit_gamma)  # or 1/summary(fit_gamma)$dispersion
```

### Python Validation Code
```python
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Load data (TBD - need appropriate dataset)
# insurance = pd.read_csv("...")

# Fit Gamma model
fit_gamma = smf.glm('amount ~ age + region + car_type',
                    data=insurance,
                    family=sm.families.Gamma(link=sm.families.links.Log())).fit()
print(fit_gamma.summary())
```

## Canonical Coefficients (TO BE VALIDATED)
```
Model: amount ~ predictors (TBD)
Family: Gamma (log link)
n = TBD observations

COEFFICIENTS (validate before building pages):
  β₀ (Intercept):    TBD
  β₁ (...):          TBD
  ...

Shape Parameter:
  shape: TBD (larger = less variance)

Model Fit:
  AIC: TBD
  Deviance: TBD
```

## IMPORTANT: The Key Comparison

The main pedagogical point is showing when Gamma beats Gaussian:

| Metric | Gaussian | Gamma |
|--------|----------|-------|
| Negative predictions | Possible | Impossible |
| Variance structure | Constant | ∝ μ² |
| Skewness | Symmetric | Right-skewed |
| Interpretation | Additive | Multiplicative (with log link) |

## Styling Reference
- Copy CSS patterns from `04-negbin/*.html`
- Use consistent header colours (red for Gamma: `#c0392b` to `#e74c3c`)
- KaTeX for math: same CDN setup as Tutorials 1-4
- Tab switching for R/Python code panels

## Navigation Links
Within tutorial: `systematic.html` ↔ `link.html` ↔ `distribution.html` ↔ `fitting.html` ↔ `code.html` ↔ `advanced.html`
Back to index: `../../index.html`

## Key Differences from Previous Tutorials

| Aspect | Tutorial 4 (NegBin) | Tutorial 5 (Gamma) |
|--------|---------------------|-------------------|
| Data type | Counts | Positive continuous |
| Distribution | Negative Binomial | Gamma |
| Support | {0, 1, 2, ...} | (0, ∞) |
| Variance | μ + μ²/θ | μ²/shape |
| Typical use | Overdispersed counts | Claim amounts, durations |
| R function | MASS::glm.nb() | glm(..., family=Gamma) |
| Python | NegativeBinomial() | Gamma() |

## Files to Reference
- `prototype/tutorials/04-negbin/` - Template structure
- `.claude/specs/tutorial-series.md` - Detailed specs
- `.claude/handover/04-negbin-tutorial.md` - Previous tutorial handover

## Update After Completion
1. Update `prototype/index.html`:
   - Change Tutorial 5 card from `unknown` to `gamma` class
   - Change "Optional" to "Complete"
   - Add link to `tutorials/05-gamma/systematic.html`
   - Change challenge-text to revealed-answer

2. Update `CLAUDE.md` status table

3. Update `.claude/specs/tutorial-series.md` status

---

## Checklist
- [ ] Find suitable insurance claims dataset
- [ ] Validate Gamma coefficients in R
- [ ] Validate Gamma coefficients in Python
- [ ] Record canonical values above
- [ ] Create systematic.html
- [ ] Create link.html
- [ ] Create distribution.html
- [ ] Create fitting.html (explain shape parameter)
- [ ] Create code.html
- [ ] Create advanced.html (Gamma likelihood derivation)
- [ ] Test all navigation links
- [ ] Update index.html
- [ ] Update CLAUDE.md status table
- [ ] Commit

---

## Notes for Next Session

### Starting Point
Read this file first. The main challenge is finding an appropriate dataset with positive continuous outcomes (insurance claim amounts, not counts).

### Dataset Considerations
- MASS::Insurance has Claims (counts), not amounts - may need transformation
- Could use synthetic data if no good public dataset
- Kaggle may have suitable insurance datasets

### Key Validation Step
Focus on comparing Gamma vs Gaussian predictions - show that Gaussian can predict negative claim amounts while Gamma cannot.

### Expected Results
- Log link coefficients give multiplicative effects (exp(β) = ratio)
- Shape parameter should be positive
- Residual deviance should be reasonable

### The Narrative Arc
T1-T2: Binary and continuous → standard cases
T3-T4: Counts with overdispersion → handling violations
T5: Positive continuous → completing the GLM family picture

### Colour Scheme
Red gradient for Gamma tutorials:
```css
.card-header.gamma {
  background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
}
```

### Alternative: Skip T5
Tutorial 5 is marked as OPTIONAL in CLAUDE.md. If the dataset proves difficult to find, this tutorial could be deferred or simplified with synthetic data.
