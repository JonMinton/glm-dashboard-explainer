# Handover: Tutorial 2 - Logistic Regression

## Task Summary
Build the complete 6-page tutorial for logistic regression (binomial GLM) following the established pattern from Tutorial 1.

## Location
Create files in: `prototype/tutorials/02-logistic/`

## Files to Create
1. `systematic.html` - Select response (target) & predictors
2. `link.html` - Choose link function (logit correct, probit semi-valid, identity/log wrong)
3. `distribution.html` - Choose distribution (Binomial correct)
4. `fitting.html` - Explain IRLS fitting (no closed-form solution)
5. `code.html` - R and Python implementation with validated outputs
6. `advanced.html` - Binomial log-likelihood derivation with KaTeX

## Key Context

### Dataset
- **Same UCI Heart Disease dataset** as Tutorial 1
- **Different outcome**: `target` (binary: 0=no disease, 1=disease)
- **Predictors**: `age`, `sex`, `cp` (chest pain type), `thalach`, `oldpeak`

### Design Pattern
Copy structure from `prototype/tutorials/01-gaussian/` but adapt content for:
- Binary outcome (not continuous)
- Logit link (not identity)
- Binomial distribution (not Gaussian)
- No closed-form solution (IRLS required)
- Odds ratio interpretation (not additive effects)

### Link Function Page - CRITICAL
Must include **4 options** with educational feedback:

| Link | Correct? | Dialog |
|------|----------|--------|
| **Logit** | ✓ Correct | Explain odds ratio interpretation |
| **Probit** | ~ Semi-valid | Historical context - dominated pre-1980s, decline with modern computation |
| **Identity** | ✗ Wrong | Predictions not bounded to (0,1) - "linear probability model" problems |
| **Log** | ✗ Wrong | Doesn't map to probability scale, allows P>1 |

### Probit Historical Context (for semi-valid dialog)
Key points to cover:
- Uses inverse standard normal CDF (Φ⁻¹) instead of log-odds
- Dominated before ~1980s in economics and bioassay
- "Latent variable" interpretation
- Logit won due to: odds ratio interpretation, algebraic simplicity, modern computation
- β_probit ≈ β_logit × 0.625
- Still used in economics (tradition) and dose-response studies

## CRITICAL: Output Validation

**DO NOT use placeholder outputs.** Before including any regression results:

1. Run actual R code:
```r
heart <- read.csv("https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data", header=FALSE)
names(heart) <- c("age","sex","cp","trestbps","chol","fbs","restecg","thalach","exang","oldpeak","slope","ca","thal","target")
heart$target <- ifelse(heart$target > 0, 1, 0)  # Binarise

fit <- glm(target ~ age + sex + cp + thalach + oldpeak,
           family = binomial(link = "logit"), data = heart)
summary(fit)
```

2. Run actual Python code:
```python
import pandas as pd
import statsmodels.formula.api as smf

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
heart = pd.read_csv(url, header=None, names=["age","sex","cp","trestbps","chol","fbs","restecg","thalach","exang","oldpeak","slope","ca","thal","target"])
heart['target'] = (heart['target'] > 0).astype(int)

fit = smf.glm('target ~ age + sex + cp + thalach + oldpeak',
              data=heart, family=sm.families.Binomial()).fit()
print(fit.summary())
```

3. Record canonical coefficient values in this file before building pages
4. Use EXACT same values on ALL pages

## Canonical Coefficients (TO BE VALIDATED)
```
Model: target ~ age + sex + cp + thalach + oldpeak
Family: binomial(link = "logit")

FILL IN AFTER RUNNING ACTUAL CODE:
  β₀ (Intercept): [TBD]
  β₁ (age):       [TBD]
  β₂ (sex):       [TBD]
  β₃ (cp):        [TBD]
  β₄ (thalach):   [TBD]
  β₅ (oldpeak):   [TBD]

  AIC: [TBD]
  Null deviance: [TBD]
  Residual deviance: [TBD]
```

## Styling Reference
- Copy CSS patterns from `01-gaussian/*.html`
- Use consistent header colours (blue for binomial: `#2980b9` to `#3498db`)
- KaTeX for math: same CDN setup as Tutorial 1
- Tab switching for R/Python code panels

## Navigation Links
Within tutorial: `systematic.html` ↔ `link.html` ↔ `distribution.html` ↔ `fitting.html` ↔ `code.html` ↔ `advanced.html`
Back to index: `../../index.html`

## Key Differences from Tutorial 1

| Aspect | Tutorial 1 (Gaussian) | Tutorial 2 (Logistic) |
|--------|----------------------|----------------------|
| Outcome | Continuous (heart rate) | Binary (disease yes/no) |
| Link | Identity: μ = η | Logit: log(p/(1-p)) = η |
| Distribution | Gaussian | Binomial |
| Coefficients mean | Additive effect (bpm) | Log-odds ratio |
| exp(β) means | N/A | Odds ratio |
| Closed form | Yes: (X'X)⁻¹X'y | No: requires IRLS |
| Dispersion | σ² estimated | Fixed at 1 |

## Files to Reference
- `prototype/tutorials/01-gaussian/` - Template structure
- `.claude/specs/tutorial-series.md` - Detailed specs including probit dialog content
- `.claude/settings.json` - Self-instructions for validation

## Update After Completion
1. Update `prototype/index.html`:
   - Change Tutorial 2 card from `unknown` to `binomial` class
   - Change "Coming Soon" to "Complete"
   - Add link to `tutorials/02-logistic/systematic.html`
   - Change challenge-text to revealed-answer

2. Update `claude.md` status table

## Checklist
- [ ] Validate coefficients in R
- [ ] Validate coefficients in Python
- [ ] Record canonical values above
- [ ] Create systematic.html
- [ ] Create link.html (with probit historical content)
- [ ] Create distribution.html
- [ ] Create fitting.html
- [ ] Create code.html
- [ ] Create advanced.html
- [ ] Test all navigation links
- [ ] Update index.html
- [ ] Commit
