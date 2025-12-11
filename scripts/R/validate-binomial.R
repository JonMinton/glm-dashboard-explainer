# Validate Tutorial 2: Binomial GLM (Logistic Regression) coefficients
# This script verifies the coefficients shown in the Binomial tutorial
# match actual R output using the UCI heart disease dataset.
#
# Expected coefficients (from tutorial):
#   Intercept: -3.1655
#   age: 0.0359
#   sex: 1.6745
#   cp: 0.8963
#   thalach: -0.0247
#   oldpeak: 0.6829

# Load the UCI Heart Disease dataset
heart <- read.csv(
  "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data",
  header = FALSE
)
names(heart) <- c("age", "sex", "cp", "trestbps", "chol", "fbs",
                  "restecg", "thalach", "exang", "oldpeak",
                  "slope", "ca", "thal", "target")

# Binarise target: 0 = no disease, 1 = disease
heart$target <- ifelse(heart$target > 0, 1, 0)

# Fit logistic regression
model <- glm(
  target ~ age + sex + cp + thalach + oldpeak,
  data = heart,
  family = binomial(link = "logit")
)

# Display results
cat("=== Binomial GLM (Logistic Regression) Validation ===\n\n")
cat("Model Summary:\n")
print(summary(model))

cat("\n\nCoefficients:\n")
print(coef(model))

# Compare to expected values
expected <- c(
  "(Intercept)" = -3.1655,
  "age" = 0.0359,
  "sex" = 1.6745,
  "cp" = 0.8963,
  "thalach" = -0.0247,
  "oldpeak" = 0.6829
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

# Additional model stats
cat("\n\nModel Fit Statistics:\n")
cat(sprintf("  Null deviance: %.2f\n", model$null.deviance))
cat(sprintf("  Residual deviance: %.2f\n", model$deviance))
cat(sprintf("  AIC: %.2f\n", AIC(model)))
cat(sprintf("  Number of iterations: %d\n", model$iter))
