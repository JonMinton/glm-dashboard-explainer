/**
 * Terrain utilities for optimization visualizations.
 * Provides elevation lookup and gradient computation for 2D terrain grids.
 */

/**
 * Get elevation at normalized coordinates (0-1) from a terrain grid.
 * Uses bilinear interpolation for smooth values between grid points.
 *
 * @param {Object} terrainData - Terrain data with elevations array and grid dimensions
 * @param {number} x - Normalized x coordinate (0-1, west to east)
 * @param {number} y - Normalized y coordinate (0-1, south to north)
 * @returns {number} Elevation at the given point
 */
export function getElevation(terrainData, x, y) {
  if (!terrainData || !terrainData.elevations) return 0;

  const cols = terrainData.grid.cols;
  const rows = terrainData.grid.rows;

  // Convert normalized coords to grid indices
  const col = x * (cols - 1);
  const row = y * (rows - 1);

  // Clamp to valid range
  const col0 = Math.max(0, Math.min(Math.floor(col), cols - 1));
  const row0 = Math.max(0, Math.min(Math.floor(row), rows - 1));
  const col1 = Math.min(col0 + 1, cols - 1);
  const row1 = Math.min(row0 + 1, rows - 1);

  // Bilinear interpolation weights
  const dx = col - col0;
  const dy = row - row0;

  // Get four corner values
  const v00 = terrainData.elevations[row0][col0];
  const v01 = terrainData.elevations[row0][col1];
  const v10 = terrainData.elevations[row1][col0];
  const v11 = terrainData.elevations[row1][col1];

  // Interpolate
  const elevation = v00 * (1 - dx) * (1 - dy) +
                    v01 * dx * (1 - dy) +
                    v10 * (1 - dx) * dy +
                    v11 * dx * dy;

  return elevation;
}

/**
 * Compute gradient of terrain at a point using central differences.
 *
 * @param {Object} terrainData - Terrain data
 * @param {number} x - Normalized x coordinate (0-1)
 * @param {number} y - Normalized y coordinate (0-1)
 * @param {number} h - Step size for finite differences (default 0.01)
 * @returns {Object} Gradient {dx, dy} in elevation units per normalized unit
 */
export function getGradient(terrainData, x, y, h = 0.01) {
  const dx = (getElevation(terrainData, x + h, y) - getElevation(terrainData, x - h, y)) / (2 * h);
  const dy = (getElevation(terrainData, x, y + h) - getElevation(terrainData, x, y - h)) / (2 * h);
  return { dx, dy };
}

/**
 * Compute the Hessian (second derivatives) at a point.
 * Returns diagonal elements only (assumes mixed partials are small).
 *
 * @param {Object} terrainData - Terrain data
 * @param {number} x - Normalized x coordinate
 * @param {number} y - Normalized y coordinate
 * @param {number} h - Step size for finite differences
 * @returns {Object} Hessian diagonal {fxx, fyy}
 */
export function getHessianDiag(terrainData, x, y, h = 0.01) {
  const f = getElevation(terrainData, x, y);
  const fxx = (getElevation(terrainData, x + h, y) - 2 * f + getElevation(terrainData, x - h, y)) / (h * h);
  const fyy = (getElevation(terrainData, x, y + h) - 2 * f + getElevation(terrainData, x, y - h)) / (h * h);
  return { fxx, fyy };
}

/**
 * Compute the full 2x2 Hessian matrix at a point.
 * Includes the off-diagonal mixed partial derivative (∂²f/∂x∂y).
 *
 * @param {Object} terrainData - Terrain data
 * @param {number} x - Normalized x coordinate
 * @param {number} y - Normalized y coordinate
 * @param {number} h - Step size for finite differences
 * @returns {Object} Full Hessian {fxx, fyy, fxy} where fxy = ∂²f/∂x∂y
 */
export function getFullHessian(terrainData, x, y, h = 0.01) {
  const f = getElevation(terrainData, x, y);

  // Second partial derivatives (diagonal)
  const fxx = (getElevation(terrainData, x + h, y) - 2 * f + getElevation(terrainData, x - h, y)) / (h * h);
  const fyy = (getElevation(terrainData, x, y + h) - 2 * f + getElevation(terrainData, x, y - h)) / (h * h);

  // Mixed partial derivative using central differences
  // fxy = (f(x+h,y+h) - f(x+h,y-h) - f(x-h,y+h) + f(x-h,y-h)) / (4h²)
  const fxy = (
    getElevation(terrainData, x + h, y + h) -
    getElevation(terrainData, x + h, y - h) -
    getElevation(terrainData, x - h, y + h) +
    getElevation(terrainData, x - h, y - h)
  ) / (4 * h * h);

  return { fxx, fyy, fxy };
}

/**
 * Compute confidence ellipse parameters from a Hessian matrix.
 * For a maximum, the negative Hessian is the observed information matrix.
 * The inverse gives the covariance matrix, from which we derive the ellipse.
 *
 * @param {Object} hessian - Hessian {fxx, fyy, fxy}
 * @param {number} confidenceLevel - Confidence level (default 0.95 for 95%)
 * @returns {Object|null} Ellipse parameters {semiMajor, semiMinor, rotation} or null if invalid
 */
export function hessianToEllipse(hessian, confidenceLevel = 0.95) {
  const { fxx, fyy, fxy } = hessian;

  // For a maximum, we negate the Hessian to get the information matrix
  // (the Hessian at a maximum is negative definite)
  const Ixx = -fxx;
  const Iyy = -fyy;
  const Ixy = -fxy;

  // Check if the information matrix is positive definite (valid maximum)
  const det = Ixx * Iyy - Ixy * Ixy;
  if (det <= 0 || Ixx <= 0) {
    // Not a valid maximum or matrix not positive definite
    return null;
  }

  // Invert to get covariance matrix
  // [Ixx Ixy]^-1 = (1/det) * [Iyy  -Ixy]
  // [Ixy Iyy]              [-Ixy  Ixx]
  const covXX = Iyy / det;
  const covYY = Ixx / det;
  const covXY = -Ixy / det;

  // Eigenvalue decomposition for ellipse axes
  // For 2x2 symmetric matrix, eigenvalues are:
  // λ = (trace ± sqrt(trace² - 4*det)) / 2
  const trace = covXX + covYY;
  const covDet = covXX * covYY - covXY * covXY;
  const discriminant = trace * trace - 4 * covDet;

  if (discriminant < 0) return null;

  const sqrtDisc = Math.sqrt(discriminant);
  const lambda1 = (trace + sqrtDisc) / 2;  // Larger eigenvalue
  const lambda2 = (trace - sqrtDisc) / 2;  // Smaller eigenvalue

  if (lambda1 <= 0 || lambda2 <= 0) return null;

  // Chi-squared critical value for 2 degrees of freedom
  // For 95%: χ² ≈ 5.991, for 90%: ≈ 4.605, for 99%: ≈ 9.210
  const chiSquaredTable = {
    0.90: 4.605,
    0.95: 5.991,
    0.99: 9.210
  };
  const chiSq = chiSquaredTable[confidenceLevel] || 5.991;

  // Semi-axes of the confidence ellipse
  const semiMajor = Math.sqrt(chiSq * lambda1);
  const semiMinor = Math.sqrt(chiSq * lambda2);

  // Rotation angle (eigenvector of larger eigenvalue)
  // For eigenvector: (A - λI)v = 0
  // If covXY ≠ 0: v1 = [covXY, λ1 - covXX] or [λ1 - covYY, covXY]
  let rotation;
  if (Math.abs(covXY) < 1e-10) {
    // Matrix is diagonal, axes align with x,y
    rotation = covXX >= covYY ? 0 : Math.PI / 2;
  } else {
    rotation = Math.atan2(lambda1 - covXX, covXY);
  }

  return {
    semiMajor,
    semiMinor,
    rotation,  // Radians, counter-clockwise from x-axis
    eigenvalues: { lambda1, lambda2 },
    covariance: { covXX, covYY, covXY }
  };
}

/**
 * Generate points for drawing a confidence ellipse.
 *
 * @param {number} cx - Centre x coordinate
 * @param {number} cy - Centre y coordinate
 * @param {number} semiMajor - Semi-major axis length
 * @param {number} semiMinor - Semi-minor axis length
 * @param {number} rotation - Rotation angle in radians
 * @param {number} numPoints - Number of points to generate (default 64)
 * @returns {Array} Array of {x, y} points forming the ellipse
 */
export function generateEllipsePoints(cx, cy, semiMajor, semiMinor, rotation, numPoints = 64) {
  const points = [];
  const cosR = Math.cos(rotation);
  const sinR = Math.sin(rotation);

  for (let i = 0; i <= numPoints; i++) {
    const theta = (2 * Math.PI * i) / numPoints;

    // Point on unrotated ellipse
    const x0 = semiMajor * Math.cos(theta);
    const y0 = semiMinor * Math.sin(theta);

    // Rotate and translate
    const x = cx + x0 * cosR - y0 * sinR;
    const y = cy + x0 * sinR + y0 * cosR;

    points.push({ x, y });
  }

  return points;
}

/**
 * Compute gradient magnitude.
 *
 * @param {Object} grad - Gradient {dx, dy}
 * @returns {number} Magnitude of gradient
 */
export function gradientMagnitude(grad) {
  return Math.sqrt(grad.dx * grad.dx + grad.dy * grad.dy);
}
