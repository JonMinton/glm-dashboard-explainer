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
