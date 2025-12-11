# Handover: Tutorial 4 - Negative Binomial Regression

## Task Summary
Build the complete 6-page tutorial for overdispersed count data (Negative Binomial GLM) following the established pattern from Tutorials 1-3. This tutorial directly continues from Tutorial 3, showing how to handle the overdispersion we discovered.

## Location
Create files in: `prototype/tutorials/04-negbin/`

## Files to Create
1. `systematic.html` - Select response (count) & predictors (same as T3)
2. `link.html` - Choose link function (log correct, same as Poisson)
3. `distribution.html` - Choose distribution (NegBin correct, Poisson wrong due to overdispersion)
4. `fitting.html` - Explain IRLS fitting with extra dispersion parameter
5. `code.html` - R and Python implementation with validated outputs
6. `advanced.html` - Negative Binomial log-likelihood derivation with KaTeX

## Key Context

### Dataset
- **Same as Tutorial 3**: UCI Bike Sharing Dataset (daily aggregates)
- **URL**: https://archive.ics.uci.edu/ml/datasets/bike+sharing+dataset
- **Outcome**: `cnt` (count of bike rentals per day, range ~22 to ~8714)
- **Predictors**: `temp`, `hum`, `windspeed`, `workingday`, `weathersit`

### The Pedagogical Story
Tutorial 3 revealed **severe overdispersion** (deviance/df = 524). This tutorial shows:
1. Why overdispersion matters (invalid inference with Poisson)
2. How Negative Binomial handles it (extra dispersion parameter θ)
3. The practical difference in standard errors and confidence intervals

### Design Pattern
Copy structure from `prototype/tutorials/03-poisson/` but adapt content for:
- Negative Binomial distribution (not Poisson)
- Extra dispersion parameter θ (theta)
- Wider standard errors (more honest uncertainty)
- Variance = μ + μ²/θ (allows variance > mean)

### Link Function Page - Options
Must include **4 options** with educational feedback:

| Link | Correct? | Dialog |
|------|----------|--------|
| **Log** | Correct | Same as Poisson - ensures positive predictions, rate ratio interpretation |
| **Identity** | Wrong | Can predict negative counts |
| **Sqrt** | Semi-valid | Historically used, less interpretable |
| **Logit** | Wrong | For probabilities, not counts |

Note: The link function choice is the same as Poisson. The key difference is the distribution.

### Distribution Page - Options

| Distribution | Correct? | Dialog |
|--------------|----------|--------|
| **Negative Binomial** | Correct | Var = μ + μ²/θ, handles overdispersion |
| **Poisson** | Wrong | We KNOW it's overdispersed from T3 (ratio = 524) |
| **Gaussian** | Wrong | Allows negative values, continuous |
| **Quasi-Poisson** | Semi-valid | Quick fix, but NegBin is proper model |

### Key Learning Points
1. Overdispersion = variance > mean (violates Poisson assumption)
2. Negative Binomial adds dispersion parameter θ
3. When θ → ∞, NegBin → Poisson (nested models)
4. Standard errors are larger (more honest) with NegBin
5. Coefficients should be similar, but inference differs

## CRITICAL: Output Validation

**DO NOT use placeholder outputs.** Before including any regression results:

1. Use the same bike sharing dataset from Tutorial 3
2. Run actual R code with MASS::glm.nb() to get real outputs
3. Run actual Python code with statsmodels NegativeBinomial to get real outputs
4. Compare coefficients between Poisson (T3) and NegBin (T4)
5. Record canonical values in this file before building pages

### R Validation Code
```r
library(MASS)

# Load bike sharing data (same as T3)
bike <- read.csv("day.csv")

# Fit Negative Binomial model
fit_nb <- glm.nb(cnt ~ temp + hum + windspeed + workingday + weathersit,
                 data = bike)
summary(fit_nb)

# Compare to Poisson from T3
fit_pois <- glm(cnt ~ temp + hum + windspeed + workingday + weathersit,
                family = poisson(link = "log"), data = bike)

# Key comparison: standard errors
cbind(Poisson_SE = summary(fit_pois)$coefficients[,2],
      NegBin_SE = summary(fit_nb)$coefficients[,2])

# Theta (dispersion parameter)
fit_nb$theta
```

### Python Validation Code
```python
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Load data
bike = pd.read_csv("day.csv")

# Fit Negative Binomial model
fit_nb = smf.glm('cnt ~ temp + hum + windspeed + workingday + weathersit',
                 data=bike,
                 family=sm.families.NegativeBinomial()).fit()
print(fit_nb.summary())

# Compare to Poisson
fit_pois = smf.glm('cnt ~ temp + hum + windspeed + workingday + weathersit',
                   data=bike,
                   family=sm.families.Poisson()).fit()

# Standard error comparison
print("Poisson SE:", fit_pois.bse)
print("NegBin SE:", fit_nb.bse)
```

## Canonical Coefficients (TO BE VALIDATED)
```
Model: cnt ~ temp + hum + windspeed + workingday + weathersit
Family: Negative Binomial (log link)
n = 731 observations

COEFFICIENTS (validate before building pages):
  β₀ (Intercept):    TBD (expect similar to Poisson: ~8.24)
  β₁ (temp):         TBD (expect similar to Poisson: ~1.40)
  β₂ (hum):          TBD (expect similar to Poisson: ~-0.36)
  β₃ (windspeed):    TBD (expect similar to Poisson: ~-0.97)
  β₄ (workingday):   TBD (expect similar to Poisson: ~0.04)
  β₅ (weathersit):   TBD (expect similar to Poisson: ~-0.13)

Standard Errors (KEY COMPARISON):
  Compare to Poisson SEs - should be MUCH larger

Dispersion Parameter:
  θ (theta): TBD (smaller θ = more overdispersion)

Model Fit:
  Log-Likelihood: TBD (should be better than Poisson)
  AIC: TBD (should be lower than Poisson: 387,415)
```

## IMPORTANT: The Key Comparison

The main pedagogical point is showing how inference changes:

| Metric | Poisson (T3) | Negative Binomial (T4) |
|--------|--------------|------------------------|
| Coefficients | ~same | ~same |
| Standard Errors | Small (wrong) | Large (honest) |
| p-values | Over-optimistic | Realistic |
| Confidence Intervals | Too narrow | Appropriate width |
| AIC | 387,415 | TBD (should be lower) |

## Styling Reference
- Copy CSS patterns from `03-poisson/*.html`
- Use consistent header colours (orange for NegBin: `#d35400` to `#e67e22`)
- KaTeX for math: same CDN setup as Tutorials 1-3
- Tab switching for R/Python code panels

## Navigation Links
Within tutorial: `systematic.html` ↔ `link.html` ↔ `distribution.html` ↔ `fitting.html` ↔ `code.html` ↔ `advanced.html`
Back to index: `../../index.html`

## Key Differences from Tutorial 3

| Aspect | Tutorial 3 (Poisson) | Tutorial 4 (Negative Binomial) |
|--------|---------------------|-------------------------------|
| Distribution | Poisson | Negative Binomial |
| Variance | = μ | = μ + μ²/θ |
| Parameters | β only | β and θ |
| Overdispersion | Detected, not handled | Properly modelled |
| Standard Errors | Underestimated | Correct |
| R function | glm(..., family=poisson) | MASS::glm.nb() |
| Python | sm.families.Poisson() | sm.families.NegativeBinomial() |

## Files to Reference
- `prototype/tutorials/03-poisson/` - Template structure (and comparison point)
- `.claude/specs/tutorial-series.md` - Detailed specs
- `.claude/handover/03-poisson-tutorial.md` - Validated Poisson coefficients for comparison

## Update After Completion
1. Update `prototype/index.html`:
   - Change Tutorial 4 card from `unknown` to `negbin` class
   - Change "Coming Soon" to "Complete"
   - Add link to `tutorials/04-negbin/systematic.html`
   - Change challenge-text to revealed-answer

2. Update `claude.md` status table

3. Update `.claude/specs/tutorial-series.md` status

---

## Checklist
- [ ] Download bike sharing dataset (or use cached from T3)
- [ ] Validate NegBin coefficients in R (MASS::glm.nb)
- [ ] Validate NegBin coefficients in Python
- [ ] Record canonical values above
- [ ] Record SE comparison (Poisson vs NegBin)
- [ ] Create systematic.html
- [ ] Create link.html
- [ ] Create distribution.html (emphasize WHY NegBin over Poisson)
- [ ] Create fitting.html (explain theta estimation)
- [ ] Create code.html (include SE comparison table)
- [ ] Create advanced.html (NegBin likelihood derivation)
- [ ] Test all navigation links
- [ ] Update index.html
- [ ] Update claude.md status table
- [ ] Commit

---

## Notes for Next Session

### Starting Point
Read this file first to understand the task scope. The bike sharing data is the same as Tutorial 3.

### Key Validation Step
Focus on the **standard error comparison** - this is the key pedagogical point. The coefficients will be similar, but the SEs should be much larger for NegBin.

### Expected Results
- Coefficients: Nearly identical to Poisson
- Standard Errors: 10-20x larger for NegBin
- AIC: Substantially lower for NegBin (better fit)
- θ: Some positive value indicating overdispersion level

### The Narrative Arc
T3 → "We fit Poisson, but discovered overdispersion"
T4 → "Here's how to fix it with Negative Binomial"

This completes the count data story (T3 + T4 together).

### Colour Scheme
Orange gradient for Negative Binomial tutorials:
```css
.card-header.negbin {
  background: linear-gradient(135deg, #d35400 0%, #e67e22 100%);
}
```

### Advanced Topic: Quasi-Poisson Alternative
In the distribution page dialog, mention Quasi-Poisson as a "quick fix" that adjusts SEs without changing the model. But NegBin is preferred because it's a proper probability model.
