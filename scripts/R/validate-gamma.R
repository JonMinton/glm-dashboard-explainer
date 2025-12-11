# Validate Tutorial 5: Gamma GLM coefficients
# This script verifies the coefficients shown in the Gamma tutorial
# match actual R output using the UCI heart disease dataset.
#
# Expected coefficients (from tutorial):
#   Intercept: 4.6460
#   age: 0.0040
#   exang: 0.0012
#   oldpeak: 0.0155
#   Shape parameter: ~61.75

# Load UCI Heart Disease data
heart <- read.csv(
  "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data",
  header = FALSE, na.strings = "?"
)
names(heart) <- c("age", "sex", "cp", "trestbps", "chol", "fbs",
                  "restecg", "thalach", "exang", "oldpeak",
                  "slope", "ca", "thal", "target")
heart <- heart[complete.cases(heart), ]

cat("Dataset dimensions:", dim(heart), "\n")
cat("Blood pressure (trestbps) summary:\n")
print(summary(heart$trestbps))

# Fit Gamma GLM with log link
model <- glm(
  trestbps ~ age + exang + oldpeak,
  data = heart,
  family = Gamma(link = "log")
)

# Display results
cat("\n=== Gamma GLM Validation ===\n\n")
cat("Model Summary:\n")
print(summary(model))

cat("\n\nCoefficients:\n")
print(coef(model))

# Shape parameter (1/dispersion)
dispersion <- summary(model)$dispersion
shape <- 1 / dispersion
cat("\n\nDispersion parameter:", dispersion, "\n")
cat("Shape parameter (1/dispersion):", shape, "\n")

# Compare to expected values
expected <- c(
  "(Intercept)" = 4.6460,
  "age" = 0.0040,
  "exang" = 0.0012,
  "oldpeak" = 0.0155
)

actual <- round(coef(model), 4)

cat("\n\nValidation Check:\n")
cat("Expected vs Actual (Coefficients):\n")
for (name in names(expected)) {
  act_val <- actual[name]
  match <- abs(expected[name] - act_val) < 0.001
  status <- if (match) "OK" else "MISMATCH"
  cat(sprintf("  %s: expected %.4f, got %.4f [%s]\n",
              name, expected[name], act_val, status))
}

# Check shape parameter
expected_shape <- 61.75
match_shape <- abs(expected_shape - shape) < 1
cat(sprintf("  shape: expected %.2f, got %.2f [%s]\n",
            expected_shape, shape, if (match_shape) "OK" else "MISMATCH"))

# Compare with Gaussian
cat("\n\nComparison with Gaussian:\n")
fit_gauss <- glm(
  trestbps ~ age + exang + oldpeak,
  data = heart,
  family = gaussian()
)

cat(sprintf("  Gamma AIC: %.1f\n", AIC(model)))
cat(sprintf("  Gaussian AIC: %.1f\n", AIC(fit_gauss)))
cat(sprintf("  Difference: %.1f (lower is better)\n", AIC(fit_gauss) - AIC(model)))

# Model fit statistics
cat("\n\nModel Fit Statistics:\n")
cat(sprintf("  Null deviance: %.4f\n", model$null.deviance))
cat(sprintf("  Residual deviance: %.4f\n", model$deviance))
