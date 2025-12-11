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

## Canonical Coefficients (VALIDATED 2025-12-11)
```
Model: target ~ age + sex + cp + thalach + oldpeak
Family: binomial(link = "logit")
n = 303 observations

VALIDATED COEFFICIENTS (R and Python match):
  β₀ (Intercept): -3.1655
  β₁ (age):        0.0359
  β₂ (sex):        1.6745
  β₃ (cp):         0.8963
  β₄ (thalach):   -0.0247
  β₅ (oldpeak):    0.6829

Standard Errors:
  SE(Intercept): 2.025
  SE(age):       0.019
  SE(sex):       0.351
  SE(cp):        0.170
  SE(thalach):   0.008
  SE(oldpeak):   0.153

Model Fit:
  Null deviance:     417.98 on 302 df
  Residual deviance: 273.13 on 297 df
  AIC: 285.13
  Log-Likelihood: -136.57
  Pseudo R² (CS): 0.38
  Fisher Scoring iterations: 5
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

## Future Improvement: Dataset Caching

**Problem:** Tutorials currently fetch datasets from UCI repository URLs. This creates a dependency on external data providers being accessible.

**Proposed Solution:** Implement conditional caching for datasets:
1. **Local fallback:** Store datasets in `data/` folder (e.g., `data/heart.csv`)
2. **Try-catch loading:** Try remote URL first, fall back to local copy
3. **Size threshold:** Only cache datasets under a certain size (e.g., <1MB)

**Implementation approaches:**
- **Pre-downloaded CSV/JSON:** Simplest - commit copies to repo in `data/` folder
- **Service worker:** PWA-style caching for offline support
- **LocalStorage/IndexedDB:** Browser-based runtime caching after first load

**R code pattern:**
```r
heart <- tryCatch(
  read.csv("https://archive.ics.uci.edu/..."),
  error = function(e) read.csv("data/heart.csv")
)
```

**Python code pattern:**
```python
try:
    heart = pd.read_csv("https://archive.ics.uci.edu/...")
except:
    heart = pd.read_csv("data/heart.csv")
```

**Note:** The `data/heart.json` file already exists but isn't currently used by tutorials.

---

## Checklist
- [x] Validate coefficients in R
- [x] Validate coefficients in Python
- [x] Record canonical values above
- [x] Create systematic.html
- [x] Create link.html (with probit historical content)
- [x] Create distribution.html
- [x] Create fitting.html
- [x] Create code.html
- [x] Create advanced.html
- [x] Test all navigation links
- [x] Update index.html
- [x] Update claude.md status table
- [x] Commit (e0d28c1)
