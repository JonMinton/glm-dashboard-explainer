Scan the specified file(s) for notation consistency.

Check that:
- Y (capital) is used for the random variable / modelled response
- y (lowercase) is used for observed data
- β is used for systematic parameters (coefficients)
- α is used for dispersion/scale parameters (σ², θ, etc.)
- η is used for linear predictor (Xβ)
- μ is used for expected value E[Y]
- g() is the link function, g⁻¹() is the inverse link
- h() is used for predictor transformations
- f() is used for the distribution family

Report any inconsistencies found.

Usage: /check-notation [file or directory]
