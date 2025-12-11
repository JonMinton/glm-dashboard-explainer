# Validate Tutorial 1: Gaussian GLM coefficients
# This script verifies the coefficients shown in the Gaussian tutorial
# match actual R output using the UCI heart disease dataset.
#
# Expected coefficients (from tutorial):
#   Intercept: 203.37
#   Age: -0.83
#   ExerciseAngina: -14.25
#   STDepression: -3.78

library(jsonlite)

# Load heart disease data
# Using UCI heart disease dataset via Kaggle-style format
heart <- fromJSON("../../data/heart.json")

# Convert ExerciseAngina to numeric if needed (1 = Yes, 0 = No)
if (is.character(heart$ExerciseAngina)) {
  heart$ExerciseAngina <- ifelse(heart$ExerciseAngina == "Y", 1, 0)
}

# Fit Gaussian GLM (equivalent to lm)
model <- glm(
  MaxHR ~ Age + ExerciseAngina + Oldpeak,
  data = heart,
  family = gaussian(link = "identity")
)

# Display results
cat("=== Gaussian GLM Validation ===\n\n")
cat("Model Summary:\n")
print(summary(model))

cat("\n\nCoefficients:\n")
print(coef(model))

# Compare to expected values
expected <- c(
  "(Intercept)" = 203.37,
  "Age" = -0.83,
  "ExerciseAngina" = -14.25,
  "Oldpeak" = -3.78
)

actual <- round(coef(model), 2)

cat("\n\nValidation Check:\n")
cat("Expected vs Actual:\n")
for (name in names(expected)) {
  match <- abs(expected[name] - actual[name]) < 0.1
  status <- if (match) "OK" else "MISMATCH"
  cat(sprintf("  %s: expected %.2f, got %.2f [%s]\n",
              name, expected[name], actual[name], status))
}
