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
 * Compute gradient magnitude.
 *
 * @param {Object} grad - Gradient {dx, dy}
 * @returns {number} Magnitude of gradient
 */
export function gradientMagnitude(grad) {
  return Math.sqrt(grad.dx * grad.dx + grad.dy * grad.dy);
}
