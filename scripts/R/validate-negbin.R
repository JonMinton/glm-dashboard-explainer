# Validate Tutorial 4: Negative Binomial GLM coefficients
# This script verifies the coefficients shown in the Negative Binomial tutorial
# match actual R output using the UCI Bike Sharing dataset.
#
# Expected coefficients (from tutorial):
#   Intercept: 8.1969
#   temp: 1.7005
#   hum: -0.4825
#   windspeed: -1.1239
#   workingday: 0.0519
#   weathersit: -0.1421
#   theta: 6.773

library(MASS)

# Load the UCI Bike Sharing dataset (daily aggregates)
bike <- read.csv("../../data/day.csv")

cat("Dataset dimensions:", dim(bike), "\n")
cat("Count summary:\n")
print(summary(bike$cnt))

# Fit Negative Binomial model using glm.nb from MASS
model <- glm.nb(
  cnt ~ temp + hum + windspeed + workingday + weathersit,
  data = bike
)

# Display results
cat("\n=== Negative Binomial GLM Validation ===\n\n")
cat("Model Summary:\n")
print(summary(model))

cat("\n\nCoefficients:\n")
print(coef(model))

cat("\n\nTheta (dispersion parameter):", model$theta, "\n")
cat("SE of Theta:", model$SE.theta, "\n")

# Compare to expected values
expected <- c(
  "(Intercept)" = 8.1969,
  "temp" = 1.7005,
  "hum" = -0.4825,
  "windspeed" = -1.1239,
  "workingday" = 0.0519,
  "weathersit" = -0.1421
)

actual <- round(coef(model), 4)

cat("\n\nValidation Check:\n")
cat("Expected vs Actual (Coefficients):\n")
for (name in names(expected)) {
  act_val <- actual[name]
  match <- abs(expected[name] - act_val) < 0.01
  status <- if (match) "OK" else "MISMATCH"
  cat(sprintf("  %s: expected %.4f, got %.4f [%s]\n",
              name, expected[name], act_val, status))
}

# Check theta
expected_theta <- 6.773
match_theta <- abs(expected_theta - model$theta) < 0.1
cat(sprintf("  theta: expected %.3f, got %.3f [%s]\n",
            expected_theta, model$theta, if (match_theta) "OK" else "MISMATCH"))

# Compare with Poisson for SE differences
cat("\n\nComparison with Poisson (SE ratios):\n")
fit_pois <- glm(cnt ~ temp + hum + windspeed + workingday + weathersit,
                family = poisson(link = "log"), data = bike)

se_pois <- summary(fit_pois)$coefficients[, 2]
se_nb <- summary(model)$coefficients[, 2]
se_ratio <- se_nb / se_pois

for (name in names(se_ratio)) {
  cat(sprintf("  %s: Poisson SE=%.4f, NegBin SE=%.4f, Ratio=%.1fx\n",
              name, se_pois[name], se_nb[name], se_ratio[name]))
}

# Model fit statistics
cat("\n\nModel Fit Statistics:\n")
cat(sprintf("  Null deviance: %.2f\n", model$null.deviance))
cat(sprintf("  Residual deviance: %.2f\n", model$deviance))
cat(sprintf("  Deviance/df: %.2f (should be ~1 for good fit)\n",
            model$deviance / model$df.residual))
cat(sprintf("  AIC (NegBin): %.2f\n", AIC(model)))
cat(sprintf("  AIC (Poisson): %.2f\n", AIC(fit_pois)))
