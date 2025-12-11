# Validate Tutorial 3: Poisson GLM coefficients
# This script verifies the coefficients shown in the Poisson tutorial
# match actual R output using the UCI Bike Sharing dataset.
#
# Expected coefficients (from tutorial):
#   Intercept: 8.2391
#   temp: 1.3971
#   hum: -0.3568
#   windspeed: -0.9673
#   workingday: 0.0389
#   weathersit: -0.1298

# Load the UCI Bike Sharing dataset (daily aggregates)
# Note: Dataset needs to be downloaded from UCI or Kaggle
bike <- read.csv("../../data/day.csv")

cat("Dataset dimensions:", dim(bike), "\n")
cat("Count summary:\n")
print(summary(bike$cnt))

# Fit Poisson regression with log link
model <- glm(
  cnt ~ temp + hum + windspeed + workingday + weathersit,
  family = poisson(link = "log"),
  data = bike
)

# Display results
cat("\n=== Poisson GLM Validation ===\n\n")
cat("Model Summary:\n")
print(summary(model))

cat("\n\nCoefficients:\n")
print(coef(model))

# Compare to expected values
expected <- c(
  "(Intercept)" = 8.2391,
  "temp" = 1.3971,
  "hum" = -0.3568,
  "windspeed" = -0.9673,
  "workingday" = 0.0389,
  "weathersit" = -0.1298
)

actual <- round(coef(model), 4)

cat("\n\nValidation Check:\n")
cat("Expected vs Actual:\n")
for (name in names(expected)) {
  act_val <- actual[name]
  match <- abs(expected[name] - act_val) < 0.01
  status <- if (match) "OK" else "MISMATCH"
  cat(sprintf("  %s: expected %.4f, got %.4f [%s]\n",
              name, expected[name], act_val, status))
}

# Check for overdispersion
cat("\n\nOverdispersion Check:\n")
dispersion_ratio <- model$deviance / model$df.residual
cat(sprintf("  Residual deviance: %.2f\n", model$deviance))
cat(sprintf("  Degrees of freedom: %d\n", model$df.residual))
cat(sprintf("  Dispersion ratio: %.2f (should be ~1 for Poisson)\n", dispersion_ratio))

if (dispersion_ratio > 2) {
  cat("  WARNING: Severe overdispersion detected! Consider Negative Binomial.\n")
}

# Additional model stats
cat("\n\nModel Fit Statistics:\n")
cat(sprintf("  Null deviance: %.2f\n", model$null.deviance))
cat(sprintf("  Residual deviance: %.2f\n", model$deviance))
cat(sprintf("  AIC: %.2f\n", AIC(model)))
