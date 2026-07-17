# Validate the R outputs shown on docs/inference/curvature.html
#
# Mirrors the JonStats "Likelihood and Simulation Theory" workflow:
# hand-rolled Gaussian log-likelihood -> optim(hessian = TRUE) ->
# solve(-hessian) -> standard errors -> mvrnorm draws,
# cross-checked against lm() / vcov().
#
# Run from scripts/R/:  Rscript validate-inference.R

library(jsonlite)

json <- fromJSON("../../docs/data/inference-rest-hr.json")
df <- json$data[1:60, ]   # the page's default sample size

y <- df$y
X <- cbind(1, df$x)

llNormal <- function(pars, y, X) {
  beta <- pars[1:ncol(X)]
  sigma2 <- exp(pars[ncol(X) + 1])
  -1/2 * sum(log(2 * pi * sigma2) + (y - (X %*% beta))^2 / sigma2)
}

fit <- optim(
  par = c(0, 0, 0),
  fn = llNormal,
  method = "BFGS",
  control = list(fnscale = -1),  # maximise, not minimise
  hessian = TRUE,
  y = y, X = X
)

cat("=== optim point estimates ===\n")
print(round(fit$par, 4))
cat("(third element is log(sigma^2); sigma-hat =",
    round(sqrt(exp(fit$par[3])), 4), ")\n\n")

cat("=== Hessian at the peak ===\n")
print(round(fit$hessian, 4))

vcov_ml <- solve(-fit$hessian)  # invert the NEGATIVE Hessian
cat("\n=== Variance-covariance matrix: solve(-hessian) ===\n")
print(round(vcov_ml, 4))

cat("\n=== Standard errors: sqrt(diag(...)) ===\n")
print(round(sqrt(diag(vcov_ml)), 4))

cat("\n=== Cross-check against lm() ===\n")
mod <- lm(y ~ x, data = df)
print(round(coef(mod), 4))
print(round(vcov(mod), 4))
print(round(sqrt(diag(vcov(mod))), 4))
cat("(lm SEs are slightly larger: lm divides the residual sum of squares",
    "\n by n - 2, maximum likelihood divides by n)\n")

cat("\n=== Simulate the sampling distribution: MASS::mvrnorm ===\n")
set.seed(42)
draws <- MASS::mvrnorm(n = 10000, mu = fit$par[1:2], Sigma = vcov_ml[1:2, 1:2])
print(round(apply(draws, 2, quantile, probs = c(0.025, 0.5, 0.975)), 4))

# ===============================================================
# Additions for the testing trio (wald.html, lr-test.html,
# model-comparison.html), 2026-07
# ===============================================================

cat("\n\n=== WALD (wald.html): summary(lm) t table, n = 60 ===\n")
print(round(summary(mod)$coefficients, 4))

cat("\n=== WALD: logistic glm z table, n = 30 ===\n")
lj <- fromJSON("../../docs/data/inference-logistic.json")
ldf <- lj$data
glm_fit <- glm(y ~ x, data = ldf, family = binomial)
print(round(summary(glm_fit)$coefficients, 4))

cat("\n=== LR TEST (lr-test.html): Gaussian full vs mean-only, n = 60 ===\n")
full <- lm(y ~ x, data = df)
restricted <- lm(y ~ 1, data = df)
cat("logLik full:      ", round(as.numeric(logLik(full)), 4), "\n")
cat("logLik mean-only: ", round(as.numeric(logLik(restricted)), 4), "\n")
lambda <- as.numeric(2 * (logLik(full) - logLik(restricted)))
cat("Lambda = ", round(lambda, 4), ", chi2(1) p = ",
    format(pchisq(lambda, 1, lower.tail = FALSE), digits = 4), "\n", sep = "")

cat("\n=== LR TEST: logistic full vs null, n = 30 ===\n")
glm_null <- glm(y ~ 1, data = ldf, family = binomial)
cat("logLik full: ", round(as.numeric(logLik(glm_fit)), 4),
    "  logLik null: ", round(as.numeric(logLik(glm_null)), 4), "\n")
print(anova(glm_null, glm_fit, test = "Chisq"))

cat("\n=== MODEL COMPARISON (model-comparison.html): AIC/BIC ladder ===\n")
mj <- fromJSON("../../docs/data/inference-model-comparison.json")
mdf <- mj$data
m0 <- lm(y ~ 1, data = mdf)
m1 <- lm(y ~ exercise, data = mdf)
m2 <- lm(y ~ exercise + age, data = mdf)
m3 <- lm(y ~ exercise + age + shoe, data = mdf)
tab <- data.frame(
  logLik = sapply(list(m0, m1, m2, m3), function(m) as.numeric(logLik(m))),
  AIC = sapply(list(m0, m1, m2, m3), AIC),
  BIC = sapply(list(m0, m1, m2, m3), BIC)
)
rownames(tab) <- c("M0: intercept", "M1: +exercise", "M2: +age", "M3: +shoe (junk)")
print(round(tab, 4))
cat("\nfull-model coefficients (M3):\n")
print(round(summary(m3)$coefficients, 4))
