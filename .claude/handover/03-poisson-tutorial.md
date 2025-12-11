# Handover: Tutorial 3 - Poisson Regression

## Task Summary
Build the complete 6-page tutorial for count data (Poisson GLM) following the established pattern from Tutorials 1 and 2.

## Location
Create files in: `prototype/tutorials/03-poisson/`

## Files to Create
1. `systematic.html` - Select response (count) & predictors
2. `link.html` - Choose link function (log correct, identity/sqrt wrong)
3. `distribution.html` - Choose distribution (Poisson correct)
4. `fitting.html` - Explain IRLS fitting
5. `code.html` - R and Python implementation with validated outputs
6. `advanced.html` - Poisson log-likelihood derivation with KaTeX

## Key Context

### Dataset
- **UCI Bike Sharing Dataset** (daily aggregates)
- **URL**: https://archive.ics.uci.edu/ml/datasets/bike+sharing+dataset
- **Outcome**: `cnt` (count of bike rentals per day, range ~22 to ~8714)
- **Predictors**: `temp`, `hum`, `windspeed`, `workingday`, `weathersit`

### Data Loading Notes
The bike sharing dataset has a slightly different structure:
- CSV with header row
- `cnt` is total count (casual + registered)
- `temp` and `atemp` are normalised (0-1 scale)
- `weathersit` is categorical (1-4)
- `workingday` is binary (0/1)

### Design Pattern
Copy structure from `prototype/tutorials/02-logistic/` but adapt content for:
- Count outcome (non-negative integers)
- Log link (not logit)
- Poisson distribution (not Binomial)
- Rate ratio interpretation (exp(β) = multiplicative effect)
- Mean = Variance assumption (key Poisson property)

### Link Function Page - Options
Must include **4 options** with educational feedback:

| Link | Correct? | Dialog |
|------|----------|--------|
| **Log** | Correct | Explain rate ratio interpretation, ensures positive predictions |
| **Identity** | Wrong | Can predict negative counts |
| **Sqrt** | Semi-valid | Variance stabilising, historically used, less interpretable |
| **Logit** | Wrong | For probabilities, not counts |

### Distribution Page - Options

| Distribution | Correct? | Dialog |
|--------------|----------|--------|
| **Poisson** | Correct | Mean = Variance, suitable for counts |
| **Gaussian** | Wrong | Allows negative values, symmetric |
| **Binomial** | Wrong | For binary/proportions, not unbounded counts |
| **Negative Binomial** | Semi-valid | Preview: handles overdispersion (Tutorial 4) |

### Key Learning Points
1. Counts can't be negative - need appropriate distribution
2. Log link: exp(β) = rate ratio (multiplicative effect)
3. Mean = Variance assumption (Poisson property)
4. Checking for overdispersion (residual deviance >> df)
5. Rate ratios vs odds ratios vs additive effects

## CRITICAL: Output Validation

**DO NOT use placeholder outputs.** Before including any regression results:

1. Download the dataset and examine structure
2. Run actual R code to get real outputs
3. Run actual Python code to get real outputs
4. Compare coefficients between implementations
5. Record canonical values in this file before building pages

### R Validation Code
```r
# Download bike sharing data (daily)
# Note: May need to download manually from UCI or use alternative source
bike <- read.csv("day.csv")  # or direct URL if available

# Inspect structure
str(bike)
summary(bike$cnt)  # Check distribution of counts

# Fit Poisson model
fit <- glm(cnt ~ temp + hum + windspeed + workingday + weathersit,
           family = poisson(link = "log"), data = bike)
summary(fit)

# Check for overdispersion
# If residual deviance >> residual df, consider negative binomial
```

### Python Validation Code
```python
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Load data
bike = pd.read_csv("day.csv")

# Fit Poisson model
fit = smf.glm('cnt ~ temp + hum + windspeed + workingday + weathersit',
              data=bike, family=sm.families.Poisson()).fit()
print(fit.summary())
```

## Canonical Coefficients (VALIDATED 2025-12-11)
```
Model: cnt ~ temp + hum + windspeed + workingday + weathersit
Family: poisson(link = "log")
n = 731 observations (2 years of daily data)

COEFFICIENTS (R and Python validated - identical):
  β₀ (Intercept):    8.2391   (SE: 0.0038)
  β₁ (temp):         1.3971   (SE: 0.0032) - positive: warmer = more rentals
  β₂ (hum):         -0.3568   (SE: 0.0053) - negative: humid = fewer rentals
  β₃ (windspeed):   -0.9673   (SE: 0.0080) - negative: windy = fewer rentals
  β₄ (workingday):   0.0389   (SE: 0.0012) - positive: working days = more rentals
  β₅ (weathersit):  -0.1298   (SE: 0.0014) - negative: bad weather = fewer

Model Fit:
  Null deviance:     668,801 on 730 df
  Residual deviance: 380,005 on 725 df
  AIC: 387,415
  Log-Likelihood: -193,700

OVERDISPERSION CHECK (critical for pedagogy):
  Ratio (resid.deviance / df): 524.1 (should be ~1 for Poisson)
  SEVERE OVERDISPERSION - perfect setup for Tutorial 4 (Negative Binomial)
```

## IMPORTANT: Overdispersion Warning

The bike sharing dataset likely shows **overdispersion** (variance > mean), which violates Poisson assumptions. This is pedagogically useful:

1. **Fit Poisson anyway** - teaches the method
2. **Show diagnostic** - residual deviance >> df
3. **Mention limitation** - "In reality, this data is overdispersed"
4. **Preview Tutorial 4** - "We'll address this with Negative Binomial"

This sets up the natural progression to Tutorial 4.

## Styling Reference
- Copy CSS patterns from `02-logistic/*.html`
- Use consistent header colours (purple for Poisson: `#8e44ad` to `#9b59b6`)
- KaTeX for math: same CDN setup as Tutorials 1-2
- Tab switching for R/Python code panels

## Navigation Links
Within tutorial: `systematic.html` ↔ `link.html` ↔ `distribution.html` ↔ `fitting.html` ↔ `code.html` ↔ `advanced.html`
Back to index: `../../index.html`

## Key Differences from Tutorial 2

| Aspect | Tutorial 2 (Logistic) | Tutorial 3 (Poisson) |
|--------|----------------------|----------------------|
| Outcome | Binary (yes/no) | Count (0, 1, 2, ...) |
| Link | Logit: log(p/(1-p)) = η | Log: log(μ) = η |
| Distribution | Binomial | Poisson |
| exp(β) means | Odds ratio | Rate ratio |
| Key assumption | None special | Mean = Variance |
| Overdispersion | N/A | Likely present (diagnostic) |

## Files to Reference
- `prototype/tutorials/02-logistic/` - Template structure
- `.claude/specs/tutorial-series.md` - Detailed specs
- `.claude/settings.json` - Self-instructions for validation

## Update After Completion
1. Update `prototype/index.html`:
   - Change Tutorial 3 card from `unknown` to `poisson` class
   - Change "Coming Soon" to "Complete"
   - Add link to `tutorials/03-poisson/systematic.html`
   - Change challenge-text to revealed-answer

2. Update `claude.md` status table

3. Update `.claude/specs/tutorial-series.md` status

---

## Checklist
- [x] Download and explore bike sharing dataset
- [x] Validate coefficients in R
- [x] Validate coefficients in Python
- [x] Record canonical values above
- [x] Create systematic.html
- [x] Create link.html (with sqrt historical context)
- [x] Create distribution.html (with NegBin preview)
- [x] Create fitting.html
- [x] Create code.html (include overdispersion diagnostic)
- [x] Create advanced.html
- [x] Test all navigation links
- [x] Update index.html
- [x] Update claude.md status table
- [x] Commit (pending)

## Dataset Caching (Future Improvement)

As noted in Tutorial 2 handover, consider implementing conditional caching:
- Store local copy in `data/bike-sharing-daily.csv`
- Try remote URL first, fall back to local
- Document data source and any preprocessing

---

## Notes for Next Session

### Starting Point
Read this file first to understand the task scope.

### Key Validation Step
The bike sharing dataset may need manual download. Check:
1. Direct UCI URL availability
2. Alternative sources (Kaggle, etc.)
3. Local cached copy if available

### Expected Challenges
1. Overdispersion will be present - document this pedagogically
2. `weathersit` might need treatment as factor/categorical
3. Count range is large (22-8714) - may want to discuss scaling

### Colour Scheme
Purple gradient for Poisson tutorials:
```css
.card-header.poisson {
  background: linear-gradient(135deg, #8e44ad 0%, #9b59b6 100%);
}
```
