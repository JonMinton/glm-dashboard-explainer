# New Sections: Tutorials + Inference + Hacker Stats

## Overview

Five new sections extending the dashboard beyond GLM family tutorials into inference and computational methods. Organised by priority.

| # | Section | Type | Pages | Priority |
|---|---------|------|-------|----------|
| 6 | Beta Regression | Tutorial (6-page) | 6 | 1 |
| 7 | Ordinal Regression | Tutorial (6-page) | 6 | 4 |
| 8 | Zero-Inflated Models | Tutorial (6-page) | 6 | 5 |
| — | Hypothesis Testing | New section (multi-page) | 4-5 | 2 |
| — | Hacker Stats | New section (multi-page) | 4-5 | 3 |

---

## Tutorial 6: Beta Regression

### Decision Problem
Predict the proportion of a student's exam questions answered correctly, given study hours and prior GPA.

### Why Beta Regression?
- Response is a **continuous proportion** bounded on (0,1) — not binary, not unbounded
- Gaussian would allow predictions outside (0,1); logistic regression treats data as binary counts
- Beta distribution naturally models rates, proportions, and percentages
- Uses the **same logit link** as logistic regression — reinforces "link function = constraint handler"
- Fills a genuine gap: neither JonStats nor current tutorials cover this

### Dataset
Synthetic or adapted dataset (n ≈ 200-300):
- **Response**: `proportion_correct` — proportion of exam questions right (0,1 exclusive)
- **Predictors**: `study_hours` (continuous, 0-20), `prior_gpa` (continuous, 2.0-4.0), `has_tutor` (binary)

Alternative real-world scenarios:
- Vote share by constituency
- Insurance loss ratio (claims paid / premiums collected)
- Proportion of time spent in REM sleep
- Soil moisture content (0-1 scale)

### Key Learning Points
- Proportions ≠ binary outcomes (0.73 is not "success")
- Logit link appears again — same transformation, different distribution
- Beta distribution: flexible shape via two parameters (α, β) or (μ, φ)
- Precision parameter φ plays the role of dispersion (like σ² for Gaussian)
- Mean-precision parameterisation: μ = α/(α+β), φ = α+β

### Link Function Page Options

| Link | Correct? | Feedback |
|------|----------|----------|
| **Logit** | ✓ Correct | Maps (0,1) to (-∞,+∞). Same as logistic regression — but now for continuous proportions, not binary outcomes |
| **Identity** | ✗ Wrong | Allows predictions outside (0,1). A model predicting 1.3 proportion correct is nonsensical |
| **Log** | ✗ Wrong | Maps to (0,∞) — prevents negatives but allows values > 1 |
| **Probit** | ~ Semi-valid | Valid alternative (same reasons as logistic regression). Results nearly identical in practice |

### Distribution Page Options

| Distribution | Correct? | Feedback |
|--------------|----------|----------|
| **Beta** | ✓ Correct | Continuous on (0,1), flexible shape. The natural choice for proportions |
| **Gaussian** | ✗ Wrong | Defined on (-∞,+∞). Predictions can exceed boundaries |
| **Binomial** | ✗ Wrong | For counts of successes out of trials, not continuous proportions |
| **Uniform** | ✗ Wrong | Assumes all proportions equally likely — no relationship with predictors |

### Why This is Pedagogically Valuable
1. **Same link, different distribution** — directly shows that link and distribution are separate choices
2. **Continuous (0,1) fills a gap** in the response-type spectrum: binary → count → positive continuous → bounded continuous
3. **Precision parameter** parallels σ² (Gaussian), θ (NegBin) — reinforces α vs β distinction
4. **Not in base R's `glm()`** — requires `betareg` package, teaching that GLMs extend beyond the core families

### R/Python Code

```r
# R
library(betareg)
fit <- betareg(proportion_correct ~ study_hours + prior_gpa + has_tutor,
               data = exam_data)
summary(fit)
# Note: betareg reports mean model (μ) and precision model (φ) separately
```

```python
# Python
import statsmodels.api as sm
# Beta regression via statsmodels (BetaModel)
from statsmodels.othermod.betareg import BetaModel
model = BetaModel(endog=exam_data['proportion_correct'],
                  exog=sm.add_constant(exam_data[['study_hours', 'prior_gpa', 'has_tutor']]))
fit = model.fit()
print(fit.summary())
```

### Advanced Page: Log-Likelihood

The Beta log-likelihood with mean-precision parameterisation:

$$\ell(\mu, \phi) = \sum_{i=1}^{n} \left[ \ln\Gamma(\phi) - \ln\Gamma(\mu_i\phi) - \ln\Gamma((1-\mu_i)\phi) + (\mu_i\phi - 1)\ln y_i + ((1-\mu_i)\phi - 1)\ln(1-y_i) \right]$$

Where μᵢ = logit⁻¹(xᵢβ) and φ is the precision parameter.

### Files

```
docs/tutorials/06-beta/
├── systematic.html    # Select response (proportion) & predictors
├── link.html          # Logit link (same as logistic — key insight)
├── distribution.html  # Beta distribution (flexible shape demo)
├── fitting.html       # MLE (no IRLS shortcut in base R)
├── code.html          # R betareg / Python BetaModel
└── advanced.html      # Beta log-likelihood derivation
```

### Dataset File
`docs/data/exam-proportions.json` — synthetic dataset

---

## Tutorial 7: Ordinal Regression

### Decision Problem
Predict a patient's self-reported pain level (None / Mild / Moderate / Severe) after treatment, given treatment type, dose, and age.

### Why Ordinal Regression?
- Response has **natural ordering** but intervals are not equal (the gap between "None" and "Mild" ≠ "Moderate" and "Severe")
- Cannot use linear regression (treating 1,2,3,4 as numeric assumes equal intervals)
- Cannot use multinomial (ignores ordering information)
- Cumulative logit model: P(Y ≤ j) = logit⁻¹(αⱼ - xβ) — multiple thresholds, one set of slopes

### Dataset
Synthetic or adapted (n ≈ 300-400):
- **Response**: `pain_level` — ordered factor (None=1, Mild=2, Moderate=3, Severe=4)
- **Predictors**: `treatment` (A/B/Placebo), `dose_mg` (continuous), `age` (continuous)

Alternative scenarios:
- Customer satisfaction (1-5 stars)
- Hurricane damage category
- Credit rating (AAA to D)
- Disease severity staging

### Key Learning Points
- Ordered categories require ordered models — treating as numeric adds false assumptions
- **Cumulative logit**: models P(Y ≤ j) using the same logit link, but with J-1 intercepts (thresholds)
- **Proportional odds assumption**: same β coefficients apply at every threshold (a single "push")
- Coefficient interpretation: exp(β) is an **odds ratio** for being in a higher vs lower category
- Threshold visualisation: the latent variable sits on a line, cut-points divide it into categories

### Link Function Page Options

| Link | Correct? | Feedback |
|------|----------|----------|
| **Cumulative logit** | ✓ Correct | Models cumulative probabilities P(Y ≤ j). Proportional odds model |
| **Logit (binary)** | ✗ Wrong | Only works for 2 categories. Would need to collapse the ordinal scale |
| **Identity** | ✗ Wrong | Treats categories as numbers with equal spacing. "Moderate" is not twice "Mild" |
| **Log** | ✗ Wrong | For counts. Pain levels are not counts |

### Distribution Page Options

| Distribution | Correct? | Feedback |
|--------------|----------|----------|
| **Cumulative (ordinal)** | ✓ Correct | Multinomial with ordering constraint. Probability distributed across ordered categories |
| **Multinomial** | ~ Semi-valid | Works but ignores ordering — less efficient, more parameters |
| **Gaussian** | ✗ Wrong | Pain level is not continuous. "2.7 pain" is meaningless |
| **Poisson** | ✗ Wrong | For counts. Categories happen to be numbered but they're not counts |

### Why This is Pedagogically Valuable
1. **Stretches the GLM framework** — multiple intercepts for one outcome. Shows GLMs can handle structured categorical data
2. **Proportional odds** is a genuinely useful concept: one β summarises the effect across all thresholds
3. **Latent variable interpretation** — connects to the probit idea from Tutorial 2 (there's a hidden continuous scale, thresholds determine observed category)
4. **Common in practice** — surveys, clinical trials, severity ratings are everywhere
5. **Not covered by JonStats** at all

### R/Python Code

```r
# R
library(MASS)
fit <- polr(pain_level ~ treatment + dose_mg + age, data = pain_data,
            method = "logistic")  # cumulative logit
summary(fit)
# Note: polr reports coefficients and intercepts (thresholds) separately
```

```python
# Python
from statsmodels.miscmodels.ordinal_model import OrderedModel
model = OrderedModel(pain_data['pain_level'],
                     pain_data[['treatment_B', 'treatment_Placebo', 'dose_mg', 'age']],
                     distr='logit')
fit = model.fit()
print(fit.summary())
```

### Advanced Page: Log-Likelihood

The cumulative logit model:
$$P(Y_i \le j) = \frac{1}{1 + \exp(-(α_j - \mathbf{x}_i\boldsymbol{\beta}))}$$

Log-likelihood:
$$\ell = \sum_{i=1}^n \sum_{j=1}^J \mathbb{1}(y_i = j) \cdot \ln\left[P(Y_i \le j) - P(Y_i \le j-1)\right]$$

Where P(Y ≤ 0) = 0 and P(Y ≤ J) = 1.

### Files

```
docs/tutorials/07-ordinal/
├── systematic.html    # Select response (ordered categories) & predictors
├── link.html          # Cumulative logit (thresholds visualised)
├── distribution.html  # Ordinal/cumulative multinomial
├── fitting.html       # MLE for proportional odds
├── code.html          # R MASS::polr / Python OrderedModel
└── advanced.html      # Cumulative logit LL derivation
```

### Interactive Elements
- **Threshold slider**: show how moving cut-points changes the category probabilities
- **Proportional odds demo**: shift β and watch all cumulative curves shift in parallel
- **Latent variable animation**: underlying continuous variable → thresholded categories

---

## Tutorial 8: Zero-Inflated Models

### Decision Problem
Predict the number of doctor visits in a year, given age, income, and insurance status — many people have zero visits (both healthy non-visitors and those who would visit but can't access care).

### Why Zero-Inflated?
- Count data with **excess zeros** that a standard Poisson or NegBin can't explain
- Two processes generate zeros: **structural zeros** (never at risk) and **sampling zeros** (at risk but count happened to be zero)
- Natural extension of Tutorials 3 (Poisson) and 4 (NegBin)
- Introduces **mixture models** — first time the dashboard shows a two-component model

### Dataset
Synthetic or adapted (n ≈ 500):
- **Response**: `doctor_visits` — count (0, 1, 2, ...) with ~40% zeros
- **Predictors**: `age` (continuous), `income` (continuous), `has_insurance` (binary), `chronic_condition` (binary)
- **Inflation predictors** (may differ): `has_insurance`, `distance_to_clinic`

Alternative scenarios:
- Number of insurance claims (many policyholders never claim)
- Fish caught per trip (some spots have no fish at all)
- Days absent from school (some students are never absent)
- Patent applications per researcher (many researchers never apply)

### Key Learning Points
- Excess zeros signal a mixture of two populations
- **Structural vs sampling zeros**: "never would" vs "could but didn't this time"
- Zero-inflated = two models in one: logistic (zero/nonzero process) + count (how many, given nonzero)
- The zero-inflation model has its own predictors (which variables predict being a "structural zero"?)
- Model comparison: Poisson vs NegBin vs ZIP vs ZINB — AIC/BIC/Vuong test

### Page Structure (Modified)

This tutorial modifies the standard 6-page flow because the key pedagogical moment is **recognising the failure of simpler models**:

```
Page 1: Systematic — select predictors (same as usual)
Page 2: Link — log link for count part (same as Poisson)
Page 3: Distribution — try Poisson first, see it fail, then introduce ZIP
Page 4: Fitting — two-component MLE (EM algorithm concept)
Page 5: Code — R pscl::zeroinfl / Python statsmodels ZeroInflatedPoisson
Page 6: Advanced — ZIP log-likelihood (mixture derivation)
```

### Distribution Page: The Diagnostic Journey

This is the key pedagogical innovation. Instead of choosing correctly on the first try, the learner:

1. **Tries Poisson** → fits model → sees poor fit diagnostic (predicted zeros << observed zeros)
2. **Tries NegBin** → better but still underpredicts zeros
3. **Sees the zero histogram** — observed zeros vs Poisson-predicted zeros vs NegBin-predicted zeros
4. **Introduces ZIP/ZINB** as the solution — a bar chart showing the mixture decomposition

### R/Python Code

```r
# R
library(pscl)
# Zero-inflated Poisson
fit_zip <- zeroinfl(doctor_visits ~ age + income + chronic_condition |
                    has_insurance + distance_to_clinic,
                    data = visits_data, dist = "poisson")
# Note: formula has two parts separated by |
#   Left of |: count model predictors
#   Right of |: zero-inflation model predictors

# Zero-inflated Negative Binomial
fit_zinb <- zeroinfl(doctor_visits ~ age + income + chronic_condition |
                     has_insurance + distance_to_clinic,
                     data = visits_data, dist = "negbin")

# Compare models
AIC(fit_poisson, fit_nb, fit_zip, fit_zinb)
vuong(fit_zip, fit_poisson)  # formal test for zero-inflation
```

```python
# Python
import statsmodels.api as sm
from statsmodels.discrete.count_model import ZeroInflatedPoisson, ZeroInflatedNegativeBinomialP

# ZIP
zip_model = ZeroInflatedPoisson(
    endog=visits_data['doctor_visits'],
    exog=sm.add_constant(visits_data[['age', 'income', 'chronic_condition']]),
    exog_infl=sm.add_constant(visits_data[['has_insurance', 'distance_to_clinic']])
)
fit_zip = zip_model.fit()
print(fit_zip.summary())
```

### Advanced Page: Log-Likelihood

ZIP log-likelihood:
$$\ell = \sum_{i=1}^n \begin{cases}
\ln\left[\pi_i + (1-\pi_i) e^{-\mu_i}\right] & \text{if } y_i = 0 \\
\ln(1-\pi_i) + y_i\ln\mu_i - \mu_i - \ln(y_i!) & \text{if } y_i > 0
\end{cases}$$

Where πᵢ = logit⁻¹(zᵢγ) is the zero-inflation probability and μᵢ = exp(xᵢβ) is the Poisson mean.

### Files

```
docs/tutorials/08-zeroinfl/
├── systematic.html    # Select response (zero-heavy count) & predictors
├── link.html          # Log link for count part + logit for zero part
├── distribution.html  # Diagnostic journey: Poisson → NegBin → ZIP
├── fitting.html       # Two-component MLE / EM concept
├── code.html          # R pscl::zeroinfl / Python ZeroInflatedPoisson
└── advanced.html      # ZIP log-likelihood (mixture decomposition)
```

### Why This is Pedagogically Valuable
1. **First mixture model** — teaches that real data can come from multiple generating processes
2. **Diagnostic thinking** — the distribution page teaches "try, fail, diagnose, fix" rather than "pick correctly"
3. **Two sets of predictors** — different variables may drive being-a-zero vs how-many-given-nonzero
4. **Builds directly on Tutorials 3-4** — learner already knows Poisson and NegBin

---

## Hypothesis Testing Section

### Overview
A new section (parallel to Tutorials and Optimisation) that teaches statistical inference — not "where is the peak?" but "how confident are we about the peak?" and "does this predictor matter?"

### Why This Section?
The dashboard currently teaches model fitting but never asks "so what?" Questions like:
- Is this coefficient significantly different from zero?
- Does adding this predictor improve the model?
- How precise is our estimate?

These are the questions practitioners actually need to answer. The infrastructure already exists — the Hessian computation for Newton-Raphson is the *same* curvature used for standard errors.

### Connection to Existing Infrastructure
- **LL surface** from optimisation pages → standard errors come from curvature at the peak
- **Hessian** already computed for Newton-Raphson → Fisher information = -E[Hessian]
- **Multiple tutorials** provide examples → can show tests in context of Gaussian, logistic, Poisson

### Page Structure

```
docs/inference/
├── index.html           # Overview: from fitting to inference
├── curvature.html       # Standard errors from the Hessian
├── wald.html            # Wald tests and confidence intervals
├── lr-test.html         # Likelihood ratio tests
└── model-comparison.html  # AIC, BIC, nested models
```

#### Page 1: From Fitting to Inference (`index.html`)

**Key idea**: The peak of the log-likelihood tells us the best parameter values. The *shape* of the peak tells us how certain we should be.

Interactive visualisation:
- 1D LL curve with a sharp peak vs a flat peak — same MLE, very different confidence
- "A sharp peak means the data strongly favour one value. A flat peak means many values are almost as good."
- Connect to the terrain metaphor: a sharp summit vs a broad plateau

Learning points:
- MLE gives point estimates; inference gives uncertainty
- The curvature at the peak encodes precision
- Preview of three approaches: Wald (local curvature), LR (compare peaks), Score (gradient at null)

#### Page 2: Standard Errors from Curvature (`curvature.html`)

**Key idea**: The second derivative (Hessian) of the LL at the MLE gives the Fisher information, whose inverse gives the variance-covariance matrix.

$$\text{Var}(\hat{\beta}) \approx \left[-\frac{\partial^2 \ell}{\partial \beta \partial \beta^\top}\right]^{-1}_{\beta=\hat{\beta}}$$

Interactive visualisation:
- 2D LL surface (from optimisation/2d.html) with the peak marked
- Hessian ellipse at the peak — already implemented in the optimisation pages
- Slider: change sample size n and watch the peak sharpen + ellipse shrink
- Slider: change true effect size and watch the peak shift

Learning points:
- SE = √(diagonal of inverse observed information)
- Larger n → sharper peak → smaller SE
- Correlation between estimates visible in the ellipse tilt (off-diagonal Hessian elements)
- **Connection**: "The Hessian that Newton-Raphson uses to take efficient steps is the *same* Hessian that gives standard errors"

Cross-link to JonStats: Likelihood and Simulation Theory page covers information matrices.

#### Page 3: Wald Tests and Confidence Intervals (`wald.html`)

**Key idea**: z = β̂/SE(β̂). If this is far from zero, the predictor matters.

Interactive visualisation:
- Normal distribution under H₀ with observed z-statistic marked
- Shaded rejection region
- Confidence interval on the LL surface: the β values within 1.96 SEs of the peak
- Toggle between 90%, 95%, 99% CI and watch the interval widen/narrow

Learning points:
- Wald test is a local approximation (only uses curvature at MLE)
- CI interpretation: "If we repeated this experiment, 95% of intervals would contain the true value"
- Connection to coefficient tables in R/Python output — every summary() table is doing Wald tests
- Limitations: Wald can be unreliable for small samples or near boundaries (Hauck-Donner effect for logistic)

#### Page 4: Likelihood Ratio Tests (`lr-test.html`)

**Key idea**: Compare the height of two peaks — full model vs restricted model. If the full model's peak is much higher, the added predictor(s) help.

$$\Lambda = 2[\ell(\hat{\beta}_{\text{full}}) - \ell(\hat{\beta}_{\text{restricted}})]$$

Interactive visualisation:
- The LL surface with two points marked: full-model peak and restricted-model peak (on a ridge/slice where the removed predictor = 0)
- The height difference is the LR statistic
- Show χ² distribution with df = number of removed predictors
- Animate adding/removing a predictor and watching the LR statistic change

Learning points:
- LR test uses global information (two peaks), not just local curvature
- Generally more reliable than Wald, especially for small samples
- The "restricted model" peak always sits lower or equal (nested models)
- df = difference in number of parameters

#### Page 5: Model Comparison (`model-comparison.html`)

**Key idea**: AIC and BIC penalise model complexity to prevent overfitting.

$$\text{AIC} = -2\ell(\hat{\beta}) + 2p \qquad \text{BIC} = -2\ell(\hat{\beta}) + p\ln(n)$$

Interactive visualisation:
- Bar chart: LL vs penalty vs AIC/BIC for nested models (1 predictor, 2 predictors, 3 predictors)
- As predictors are added, LL always increases but penalty increases too
- The optimal model minimises AIC/BIC — usually not the most complex

Learning points:
- AIC ≈ "prediction accuracy" (Kullback-Leibler)
- BIC ≈ "which model generated the data?" (Bayesian)
- BIC penalises complexity more than AIC, especially for large n
- Not a hypothesis test — no p-value, no rejection. Just ranking.
- Connection to Tutorial 4 (NegBin) where AIC was used to compare Poisson vs NegBin

### Cross-Links
- **From tutorials**: Each tutorial's fitting/code page could link to the inference section: *"Now you've fitted the model — but how confident are you in these coefficients? See [Inference: From Fitting to Testing](../inference/)"*
- **From optimisation**: The bridge page and 2d/3d pages could link to curvature.html: *"The Hessian ellipse doesn't just help algorithms converge — it gives standard errors"*
- **To JonStats**: Likelihood and Simulation Theory already covers information matrices and variance-covariance matrices

---

## Hacker Stats Section

### Overview
A new section introducing computational (non-parametric) approaches to inference: bootstrap and permutation testing. Methodologically orthogonal to everything else on the dashboard — no distributional assumptions, no log-likelihood, no link functions. Pure computation.

### Why This Section?
1. **Different philosophy**: "Don't assume a distribution — let the data speak via resampling"
2. **Validates parametric results**: When bootstrap CIs agree with Wald CIs, both are trustworthy. When they disagree, something interesting is happening.
3. **Complements the hypothesis testing section**: parametric (Wald/LR) vs computational (bootstrap/permutation) approaches to the same questions
4. **Visually compelling**: resampled distributions and permutation null distributions are naturally interactive
5. **JonStats covers this in R** — the dashboard adds the interactive/visual dimension

### Page Structure

```
docs/hacker-stats/
├── index.html           # Why resample? The computational alternative
├── bootstrap.html       # Bootstrap confidence intervals
├── permutation.html     # Permutation tests
├── comparison.html      # Parametric vs computational side-by-side
└── when-to-use.html     # When does it matter?
```

#### Page 1: Why Resample? (`index.html`)

**Key idea**: Instead of deriving the sampling distribution mathematically, approximate it by resampling from the data you have.

Interactive visualisation:
- A small dataset (n=20) shown as points
- Button: "Resample" — draw n=20 points with replacement, show which points were picked (some twice, some not at all)
- Fit a simple model (e.g., mean, or slope) to the resample
- Repeat 100 times → show the distribution of resampled statistics
- Compare to the theoretical sampling distribution (if known)

Learning points:
- The bootstrap principle: the sample is to the population as the resample is to the sample
- No distributional assumptions needed
- Works for *any* statistic, not just means (medians, ratios, custom functions)
- Requires only one thing: that the sample is representative

#### Page 2: Bootstrap Confidence Intervals (`bootstrap.html`)

**Key idea**: Fit the model B times on resampled datasets. The distribution of β̂* gives a confidence interval.

Interactive visualisation:
- Using Tutorial 1 (Gaussian) or Tutorial 2 (Logistic) data
- Left panel: the original data and fitted line/curve
- Right panel: 200 bootstrap resamples shown as faint lines, with 95% CI band
- Below: histogram of bootstrap β̂* values with percentile CI marked
- Side-by-side comparison: bootstrap CI vs Wald CI (from curvature)
- Slider: change B (number of resamples) and watch the CI stabilise

Learning points:
- Percentile method: 2.5th and 97.5th percentiles of bootstrap distribution
- BCa (bias-corrected and accelerated) briefly mentioned as improvement
- Bootstrap CIs don't assume symmetry — they can be asymmetric
- For large samples with well-behaved data, bootstrap ≈ Wald. The difference shows up for small n, skewed data, or near boundaries.

#### Page 3: Permutation Tests (`permutation.html`)

**Key idea**: To test whether X predicts Y, break the X-Y relationship by shuffling Y, and see how extreme your observed statistic is compared to the shuffled distribution.

Interactive visualisation:
- Scatter plot of X vs Y with observed slope marked
- Button: "Permute" — shuffle Y labels, refit, show the new (null) slope
- Repeat 1000 times → build the permutation null distribution
- Mark the observed slope on the null distribution → visual p-value
- Animate: the data points stay fixed, the Y labels get reshuffled

Learning points:
- Permutation tests directly answer: "Could this pattern arise by chance?"
- The null distribution is exact (not approximate like χ² or z)
- No distributional assumptions at all
- Fisher's exact test and the classic t-test permutation are special cases
- Two-sided vs one-sided: how to count "as extreme or more extreme"

#### Page 4: Parametric vs Computational (`comparison.html`)

**Key idea**: Run the same analysis both ways. When do the results agree? When do they diverge?

Interactive visualisation:
- Choose a tutorial dataset (Gaussian, Logistic, Poisson)
- Left column: parametric inference (Wald test, LR test, analytic CI)
- Right column: computational inference (bootstrap CI, permutation p-value)
- Results table showing both side by side
- Scenario toggles:
  - **Large n, well-behaved**: parametric ≈ computational (both valid)
  - **Small n**: bootstrap may give wider, asymmetric CIs
  - **Outliers present**: bootstrap is more robust
  - **Near boundary**: bootstrap handles better (e.g., proportion near 0 or 1)

Learning points:
- Agreement = both methods are reliable
- Disagreement = investigate further (which assumptions are violated?)
- Computational methods are not "better" — they trade theoretical elegance for generality
- Both have limitations: bootstrap needs representative samples, permutation tests a specific null

#### Page 5: When Does It Matter? (`when-to-use.html`)

**Key idea**: Decision guide for practitioners.

Content (not heavily interactive — mostly text with examples):

| Situation | Parametric | Computational | Recommendation |
|-----------|------------|---------------|----------------|
| Large n, GLM assumptions met | Fast, exact SEs | Slower, same answer | Parametric (simpler) |
| Small n (< 30) | SEs may be wrong | More reliable CIs | Bootstrap |
| Skewed response, few predictors | May misspecify variance | Robust | Bootstrap |
| Testing H₀: β = 0 | Wald/LR test | Permutation test | Either (agree usually) |
| Complex statistic (median, ratio) | No formula available | Works for any stat | Bootstrap (only option) |
| Near boundary (proportion ≈ 0) | Wald CI can go negative | Stays in bounds | Bootstrap |

Cross-link: "When in doubt, run both. If they agree, report the parametric results (more familiar). If they disagree, investigate why."

### Implementation Notes
- Reuse datasets from existing tutorials (no new datasets needed for comparison page)
- Bootstrap/permutation algorithms are pure JS — no external libraries needed
- Animations should be interruptible (user can pause mid-resample)
- Performance: 1000 bootstrap resamples of n=300 is fast in JS, but may need Web Workers for B=10000

### Cross-Links
- **From tutorials**: Link from code pages: *"Want to check these results without distributional assumptions? See [Bootstrap Confidence Intervals](../hacker-stats/bootstrap.html)"*
- **From inference section**: comparison.html directly links parametric ↔ computational
- **To JonStats**: Hacker Stats supplementary course covers the same concepts in R code

---

## Implementation Order

### Phase 1: Foundations
1. **Hypothesis Testing** (pages 1-2: index + curvature) — builds on existing optimisation infrastructure
2. **Beta Regression** tutorial — cleanest new tutorial, follows existing 6-page pattern exactly

### Phase 2: Core
3. **Hypothesis Testing** (pages 3-5: Wald, LR, model comparison) — completes inference section
4. **Hacker Stats** (pages 1-3: index, bootstrap, permutation) — core computational methods

### Phase 3: Extensions
5. **Hacker Stats** (pages 4-5: comparison, when-to-use) — ties parametric + computational together
6. **Ordinal Regression** tutorial
7. **Zero-Inflated Models** tutorial

### Dependencies
- Hypothesis testing curvature page reuses Hessian code from optimisation pages
- Hacker Stats comparison page depends on hypothesis testing section existing
- Zero-inflated tutorial references Tutorials 3 and 4 (Poisson, NegBin)
- All new tutorials need synthetic/adapted datasets created and validated

---

## Updates to Site Navigation

### index.html (Tutorial Index)
Add two new navigation sections alongside "GLM Tutorials" and "Optimisation":

```
Statistical Inference    →  docs/inference/
  From Fitting to Inference
  Standard Errors from Curvature
  Wald Tests & Confidence Intervals
  Likelihood Ratio Tests
  Model Comparison (AIC/BIC)

Computational Methods    →  docs/hacker-stats/
  Why Resample?
  Bootstrap Confidence Intervals
  Permutation Tests
  Parametric vs Computational
  When Does It Matter?
```

### Suggested Site Map (after all additions)

```
GLM Dashboard Explainer
├── GLM Tutorials (1-8)
│   ├── 01 Gaussian         ← COMPLETE
│   ├── 02 Logistic         ← COMPLETE
│   ├── 03 Poisson          ← COMPLETE
│   ├── 04 Negative Binomial ← COMPLETE
│   ├── 05 Gamma            ← COMPLETE
│   ├── 06 Beta             ← NEW
│   ├── 07 Ordinal          ← NEW
│   └── 08 Zero-Inflated    ← NEW
├── Optimisation Visualised
│   ├── 1D Mean-Only        ← COMPLETE
│   ├── 2D Line Fitting     ← COMPLETE
│   ├── 3D Multiple Regression ← COMPLETE
│   ├── 4D+ Beyond Vis      ← COMPLETE
│   ├── Multi-Optima         ← COMPLETE
│   ├── MCMC                 ← COMPLETE
│   └── Terrain = Likelihood ← COMPLETE (bridge page)
├── Statistical Inference    ← NEW SECTION
│   ├── From Fitting to Inference
│   ├── Standard Errors from Curvature
│   ├── Wald Tests & CIs
│   ├── Likelihood Ratio Tests
│   └── Model Comparison
└── Computational Methods    ← NEW SECTION
    ├── Why Resample?
    ├── Bootstrap CIs
    ├── Permutation Tests
    ├── Parametric vs Computational
    └── When Does It Matter?
```

---

## CROSS-LINKS.md Additions

### JonStats → GLM Dashboard (new links)

**Hacker Stats supplementary course** → `docs/hacker-stats/`
> *"See these resampling methods visualised interactively: [Bootstrap & Permutation Testing](https://jonminton.github.io/glm-dashboard-explainer/hacker-stats/)"*

**P-Values and Statistical Significance** → `docs/inference/`
> *"For an interactive exploration of Wald tests, LR tests, and model comparison: [Statistical Inference](https://jonminton.github.io/glm-dashboard-explainer/inference/)"*

### GLM Dashboard → JonStats (new links)

**Inference section** → JonStats P-Values course + Likelihood Theory
**Hacker Stats section** → JonStats Hacker Stats course
