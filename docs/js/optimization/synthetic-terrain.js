/**
 * Synthetic terrain generators for optimization visualizations.
 * Creates simple landscapes with known properties for pedagogical demonstrations.
 */

/**
 * Seeded pseudo-random number generator (Mulberry32).
 * Provides reproducible random sequences for fixed seeds.
 *
 * @param {number} seed - Integer seed
 * @returns {Function} Function that returns random numbers in [0, 1)
 */
export function createRNG(seed) {
  return function() {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

/**
 * Generate a unimodal Gaussian bump terrain.
 * Single peak with controllable position, height, and spread.
 *
 * @param {Object} options - Configuration options
 * @param {number} options.peakX - X position of peak (0-1, default 0.5)
 * @param {number} options.peakY - Y position of peak (0-1, default 0.5)
 * @param {number} options.peakHeight - Maximum elevation (default 250)
 * @param {number} options.baseHeight - Minimum elevation (default 50)
 * @param {number} options.sigmaX - Spread in X direction (default 0.2)
 * @param {number} options.sigmaY - Spread in Y direction (default 0.2)
 * @param {number} options.rotation - Rotation angle in radians (default 0)
 * @param {number} options.gridSize - Number of grid points per axis (default 100)
 * @returns {Object} Terrain data in standard format
 */
export function createUnimodalTerrain(options = {}) {
  const {
    peakX = 0.5,
    peakY = 0.5,
    peakHeight = 250,
    baseHeight = 50,
    sigmaX = 0.2,
    sigmaY = 0.2,
    rotation = 0,
    gridSize = 100
  } = options;

  const elevations = [];
  const cosR = Math.cos(rotation);
  const sinR = Math.sin(rotation);

  for (let row = 0; row < gridSize; row++) {
    const rowData = [];
    const y = row / (gridSize - 1);

    for (let col = 0; col < gridSize; col++) {
      const x = col / (gridSize - 1);

      // Translate to peak-centred coordinates
      const dx = x - peakX;
      const dy = y - peakY;

      // Apply rotation
      const dxRot = dx * cosR + dy * sinR;
      const dyRot = -dx * sinR + dy * cosR;

      // Gaussian bump
      const exponent = -(dxRot * dxRot) / (2 * sigmaX * sigmaX)
                       -(dyRot * dyRot) / (2 * sigmaY * sigmaY);
      const elevation = baseHeight + (peakHeight - baseHeight) * Math.exp(exponent);

      rowData.push(elevation);
    }
    elevations.push(rowData);
  }

  return {
    elevations,
    grid: {
      rows: gridSize,
      cols: gridSize
    },
    stats: {
      min: baseHeight,
      max: peakHeight
    },
    metadata: {
      type: 'unimodal',
      peaks: [{ x: peakX, y: peakY, height: peakHeight }],
      params: { peakX, peakY, peakHeight, baseHeight, sigmaX, sigmaY, rotation }
    }
  };
}

/**
 * Generate a bimodal terrain with two peaks.
 * Useful for demonstrating local vs global optima.
 *
 * @param {Object} options - Configuration options
 * @param {Object} options.peak1 - First peak {x, y, height, sigmaX, sigmaY}
 * @param {Object} options.peak2 - Second peak {x, y, height, sigmaX, sigmaY}
 * @param {number} options.baseHeight - Minimum elevation (default 50)
 * @param {number} options.gridSize - Grid resolution (default 100)
 * @returns {Object} Terrain data in standard format
 */
export function createBimodalTerrain(options = {}) {
  const {
    peak1 = { x: 0.3, y: 0.6, height: 200, sigmaX: 0.12, sigmaY: 0.12 },
    peak2 = { x: 0.7, y: 0.4, height: 250, sigmaX: 0.15, sigmaY: 0.15 },
    baseHeight = 50,
    gridSize = 100
  } = options;

  const elevations = [];
  const maxHeight = Math.max(peak1.height, peak2.height);

  for (let row = 0; row < gridSize; row++) {
    const rowData = [];
    const y = row / (gridSize - 1);

    for (let col = 0; col < gridSize; col++) {
      const x = col / (gridSize - 1);

      // Contribution from each peak
      const dx1 = x - peak1.x;
      const dy1 = y - peak1.y;
      const z1 = (peak1.height - baseHeight) * Math.exp(
        -(dx1 * dx1) / (2 * peak1.sigmaX * peak1.sigmaX)
        -(dy1 * dy1) / (2 * peak1.sigmaY * peak1.sigmaY)
      );

      const dx2 = x - peak2.x;
      const dy2 = y - peak2.y;
      const z2 = (peak2.height - baseHeight) * Math.exp(
        -(dx2 * dx2) / (2 * peak2.sigmaX * peak2.sigmaX)
        -(dy2 * dy2) / (2 * peak2.sigmaY * peak2.sigmaY)
      );

      // Sum contributions (additive model)
      const elevation = baseHeight + z1 + z2;
      rowData.push(elevation);
    }
    elevations.push(rowData);
  }

  // Determine actual max (peaks can overlap)
  let actualMax = baseHeight;
  for (const row of elevations) {
    for (const val of row) {
      if (val > actualMax) actualMax = val;
    }
  }

  return {
    elevations,
    grid: {
      rows: gridSize,
      cols: gridSize
    },
    stats: {
      min: baseHeight,
      max: actualMax
    },
    metadata: {
      type: 'bimodal',
      peaks: [
        { x: peak1.x, y: peak1.y, height: peak1.height },
        { x: peak2.x, y: peak2.y, height: peak2.height }
      ],
      globalPeak: peak1.height > peak2.height ? peak1 : peak2,
      params: { peak1, peak2, baseHeight }
    }
  };
}

/**
 * Generate a ridge terrain (elongated peak).
 * Useful for demonstrating how Hessian approximation fails with non-circular optima.
 *
 * @param {Object} options - Configuration options
 * @param {number} options.ridgeX - X position of ridge centre (default 0.5)
 * @param {number} options.ridgeY - Y position of ridge centre (default 0.5)
 * @param {number} options.ridgeHeight - Peak height (default 250)
 * @param {number} options.baseHeight - Base elevation (default 50)
 * @param {number} options.sigmaParallel - Spread along ridge (default 0.4)
 * @param {number} options.sigmaPerpendicular - Spread across ridge (default 0.08)
 * @param {number} options.rotation - Ridge orientation in radians (default π/4)
 * @param {number} options.gridSize - Grid resolution (default 100)
 * @returns {Object} Terrain data
 */
export function createRidgeTerrain(options = {}) {
  const {
    ridgeX = 0.5,
    ridgeY = 0.5,
    ridgeHeight = 250,
    baseHeight = 50,
    sigmaParallel = 0.4,
    sigmaPerpendicular = 0.08,
    rotation = Math.PI / 4,
    gridSize = 100
  } = options;

  // A ridge is just a very elongated Gaussian
  return createUnimodalTerrain({
    peakX: ridgeX,
    peakY: ridgeY,
    peakHeight: ridgeHeight,
    baseHeight,
    sigmaX: sigmaParallel,
    sigmaY: sigmaPerpendicular,
    rotation,
    gridSize
  });
}

/**
 * Generate a synthetic approximation of Arthur's Seat, Edinburgh.
 * Sum of 5 Gaussian bumps capturing the main topographic features:
 * - Arthur's Seat summit (~238m, western side)
 * - Shoulder northeast of summit
 * - Salisbury Crags ridge (elongated NNW-SSE)
 * - Broad Holyrood Park base elevation
 * - Western slopes
 *
 * @param {number} gridSize - Grid resolution (default 100)
 * @returns {Object} Terrain data in standard format
 */
export function createArthursSeatSynthetic(gridSize = 100) {
  const bumps = [
    { cx: 0.20, cy: 0.62, height: 128, sx: 0.06, sy: 0.07, rot: 0.3 },   // Summit
    { cx: 0.25, cy: 0.67, height: 50,  sx: 0.07, sy: 0.05, rot: 0.5 },   // Shoulder
    { cx: 0.32, cy: 0.48, height: 80,  sx: 0.05, sy: 0.18, rot: 0.2 },   // Salisbury Crags
    { cx: 0.25, cy: 0.50, height: 30,  sx: 0.20, sy: 0.25, rot: 0.0 },   // Park base
    { cx: 0.08, cy: 0.55, height: 15,  sx: 0.10, sy: 0.20, rot: 0.0 },   // Western slopes
  ];
  const baseHeight = 30;

  const elevations = [];
  let actualMax = baseHeight;

  for (let row = 0; row < gridSize; row++) {
    const rowData = [];
    const y = row / (gridSize - 1);

    for (let col = 0; col < gridSize; col++) {
      const x = col / (gridSize - 1);
      let z = baseHeight;

      for (const b of bumps) {
        const dx = x - b.cx;
        const dy = y - b.cy;
        const cosR = Math.cos(b.rot);
        const sinR = Math.sin(b.rot);
        const dxRot = dx * cosR + dy * sinR;
        const dyRot = -dx * sinR + dy * cosR;
        const exponent = -(dxRot * dxRot) / (2 * b.sx * b.sx)
                         -(dyRot * dyRot) / (2 * b.sy * b.sy);
        z += b.height * Math.exp(exponent);
      }

      if (z > actualMax) actualMax = z;
      rowData.push(z);
    }
    elevations.push(rowData);
  }

  return {
    elevations,
    grid: { rows: gridSize, cols: gridSize },
    stats: { min: baseHeight, max: actualMax },
    metadata: {
      type: 'arthurs-seat-synthetic',
      description: "Smooth approximation of Arthur's Seat, Edinburgh"
    }
  };
}

/**
 * Preset terrain configurations for common pedagogical scenarios.
 */
export const TERRAIN_PRESETS = {
  // Simple unimodal - good for demonstrating basic optimization
  'simple-peak': () => createUnimodalTerrain({
    peakX: 0.5,
    peakY: 0.5,
    peakHeight: 250,
    baseHeight: 50,
    sigmaX: 0.2,
    sigmaY: 0.2
  }),

  // Asymmetric peak - shows direction-dependent convergence
  'asymmetric-peak': () => createUnimodalTerrain({
    peakX: 0.5,
    peakY: 0.5,
    peakHeight: 250,
    baseHeight: 50,
    sigmaX: 0.3,
    sigmaY: 0.1,
    rotation: Math.PI / 6
  }),

  // Two peaks - local vs global optima
  'two-peaks': () => createBimodalTerrain({
    peak1: { x: 0.3, y: 0.65, height: 200, sigmaX: 0.12, sigmaY: 0.12 },
    peak2: { x: 0.7, y: 0.35, height: 250, sigmaX: 0.15, sigmaY: 0.15 },
    baseHeight: 50
  }),

  // Sharp ridge - Hessian approximation fails badly
  'sharp-ridge': () => createRidgeTerrain({
    ridgeX: 0.5,
    ridgeY: 0.5,
    ridgeHeight: 250,
    baseHeight: 50,
    sigmaParallel: 0.35,
    sigmaPerpendicular: 0.05,
    rotation: Math.PI / 4
  }),

  // Gentle ridge - Hessian works reasonably
  'gentle-ridge': () => createRidgeTerrain({
    ridgeX: 0.5,
    ridgeY: 0.5,
    ridgeHeight: 250,
    baseHeight: 50,
    sigmaParallel: 0.25,
    sigmaPerpendicular: 0.15,
    rotation: Math.PI / 4
  }),

  // Arthur's Seat synthetic - recognisable Edinburgh landmark
  'arthurs-seat': () => createArthursSeatSynthetic()
};

/**
 * Get a preset terrain by name.
 *
 * @param {string} presetName - Name of the preset
 * @returns {Object} Terrain data
 */
export function getPresetTerrain(presetName) {
  const factory = TERRAIN_PRESETS[presetName];
  if (!factory) {
    throw new Error(`Unknown terrain preset: ${presetName}. Available: ${Object.keys(TERRAIN_PRESETS).join(', ')}`);
  }
  return factory();
}
