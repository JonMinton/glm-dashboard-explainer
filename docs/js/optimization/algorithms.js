/**
 * Optimization algorithms for finding maxima of objective functions.
 * All algorithms work with generic objective functions in normalized [0,1]^2 space.
 */

import { getGradient, getHessianDiag, gradientMagnitude } from './terrain.js';

/**
 * Configuration defaults for algorithms.
 */
export const DEFAULTS = {
  gradientAscent: {
    stepSize: 0.008,
    convergenceTol: 0.5,
  },
  newtonRaphson: {
    convergenceTol: 0.3,
    damping: 0.5,
    maxStep: 0.08,
    hessianThreshold: -0.1,
    fallbackStepSize: 0.005,
  },
  simulatedAnnealing: {
    initialTemp: 1.0,
    coolingRate: 0.995,
    minTemp: 0.01,
    stepScale: 0.05,
    tempScale: 50,
  },
  randomRestarts: {
    maxRestarts: 5,
    maxIterPerRestart: 50,
  },
};

/**
 * Clamp a position to [0,1] bounds.
 */
function clamp(x, min = 0, max = 1) {
  return Math.max(min, Math.min(max, x));
}

/**
 * Gradient Ascent step.
 * Takes a fixed-size step in the direction of steepest ascent.
 *
 * @param {Object} state - Current state {x, y, elevation, ...}
 * @param {Object} terrainData - Terrain data for elevation lookup
 * @param {Function} getElev - Function to get elevation at (x, y)
 * @param {Object} config - Algorithm configuration
 * @returns {Object} Updated state with convergence info
 */
export function stepGradientAscent(state, terrainData, getElev, config = {}) {
  const opts = { ...DEFAULTS.gradientAscent, ...config };

  const grad = getGradient(terrainData, state.x, state.y);
  const magnitude = gradientMagnitude(grad);

  // Check convergence
  if (magnitude < opts.convergenceTol) {
    return {
      ...state,
      converged: true,
      convergenceReason: 'gradient_small',
    };
  }

  // Normalize step to have consistent speed
  const stepX = (grad.dx / magnitude) * opts.stepSize;
  const stepY = (grad.dy / magnitude) * opts.stepSize;

  const newX = clamp(state.x + stepX);
  const newY = clamp(state.y + stepY);

  return {
    ...state,
    x: newX,
    y: newY,
    elevation: getElev(newX, newY),
    iteration: state.iteration + 1,
    stepSize: opts.stepSize,
    gradientMagnitude: magnitude,
  };
}

/**
 * Newton-Raphson step.
 * Uses second derivatives for faster convergence near optima.
 * Step size naturally decreases as gradient approaches zero.
 *
 * @param {Object} state - Current state {x, y, elevation, ...}
 * @param {Object} terrainData - Terrain data
 * @param {Function} getElev - Function to get elevation
 * @param {Object} config - Algorithm configuration
 * @returns {Object} Updated state
 */
export function stepNewtonRaphson(state, terrainData, getElev, config = {}) {
  const opts = { ...DEFAULTS.newtonRaphson, ...config };
  const h = 0.01;

  const grad = getGradient(terrainData, state.x, state.y, h);
  const magnitude = gradientMagnitude(grad);

  // Convergence check
  if (magnitude < opts.convergenceTol) {
    return {
      ...state,
      converged: true,
      convergenceReason: 'gradient_small',
    };
  }

  // Get Hessian diagonal
  const hess = getHessianDiag(terrainData, state.x, state.y, h);

  // Compute Newton step when Hessian is well-conditioned
  let stepX, stepY;

  if (hess.fxx < opts.hessianThreshold) {
    // Newton step: -grad/H (H is negative for maximum)
    stepX = -grad.dx / hess.fxx;
  } else {
    // Ill-conditioned: fall back to gradient ascent
    stepX = grad.dx * opts.fallbackStepSize;
  }

  if (hess.fyy < opts.hessianThreshold) {
    stepY = -grad.dy / hess.fyy;
  } else {
    stepY = grad.dy * opts.fallbackStepSize;
  }

  // Apply damping
  stepX *= opts.damping;
  stepY *= opts.damping;

  // Safety clamp
  stepX = clamp(stepX, -opts.maxStep, opts.maxStep);
  stepY = clamp(stepY, -opts.maxStep, opts.maxStep);

  const newX = clamp(state.x + stepX);
  const newY = clamp(state.y + stepY);
  const actualStep = Math.sqrt(stepX * stepX + stepY * stepY);

  return {
    ...state,
    x: newX,
    y: newY,
    elevation: getElev(newX, newY),
    iteration: state.iteration + 1,
    stepSize: actualStep,
    gradientMagnitude: magnitude,
    hessian: hess,
  };
}

/**
 * Simulated Annealing step.
 * Probabilistically accepts worse solutions to escape local optima.
 *
 * @param {Object} state - Current state {x, y, elevation, temperature, ...}
 * @param {Object} terrainData - Terrain data (unused, kept for interface consistency)
 * @param {Function} getElev - Function to get elevation
 * @param {Object} config - Algorithm configuration
 * @returns {Object} Updated state
 */
export function stepSimulatedAnnealing(state, terrainData, getElev, config = {}) {
  const opts = { ...DEFAULTS.simulatedAnnealing, ...config };

  // Check if cooled
  if (state.temperature < opts.minTemp) {
    return {
      ...state,
      converged: true,
      convergenceReason: 'temperature_min',
      x: state.bestX,
      y: state.bestY,
      elevation: state.bestElevation,
    };
  }

  // Propose random move scaled by temperature
  const stepSize = opts.stepScale * state.temperature;
  const proposedX = clamp(state.x + (Math.random() - 0.5) * stepSize);
  const proposedY = clamp(state.y + (Math.random() - 0.5) * stepSize);
  const proposedElev = getElev(proposedX, proposedY);

  // Metropolis acceptance criterion
  const delta = proposedElev - state.elevation;
  const acceptProb = delta > 0 ? 1 : Math.exp(delta / (state.temperature * opts.tempScale));

  let newX = state.x;
  let newY = state.y;
  let newElev = state.elevation;
  let accepted = false;

  if (Math.random() < acceptProb) {
    newX = proposedX;
    newY = proposedY;
    newElev = proposedElev;
    accepted = true;
  }

  // Update best if improved
  let bestX = state.bestX;
  let bestY = state.bestY;
  let bestElev = state.bestElevation;

  if (newElev > bestElev) {
    bestX = newX;
    bestY = newY;
    bestElev = newElev;
  }

  return {
    ...state,
    x: newX,
    y: newY,
    elevation: newElev,
    temperature: state.temperature * opts.coolingRate,
    iteration: state.iteration + 1,
    bestX,
    bestY,
    bestElevation: bestElev,
    accepted,
    delta,
  };
}

/**
 * Random Restarts step.
 * Runs gradient ascent from multiple random starting points.
 *
 * @param {Object} state - Current state
 * @param {Object} terrainData - Terrain data
 * @param {Function} getElev - Function to get elevation
 * @param {Object} config - Algorithm configuration
 * @returns {Object} Updated state
 */
export function stepRandomRestarts(state, terrainData, getElev, config = {}) {
  const opts = { ...DEFAULTS.randomRestarts, ...config };

  const grad = getGradient(terrainData, state.x, state.y);
  const magnitude = gradientMagnitude(grad);
  const localIteration = state.iteration - state.restarts * opts.maxIterPerRestart;

  // Check if current restart converged or hit iteration limit
  if (magnitude < 0.5 || localIteration >= opts.maxIterPerRestart) {
    const newRestarts = state.restarts + 1;

    // Update best if current is better
    let bestX = state.bestX;
    let bestY = state.bestY;
    let bestElev = state.bestElevation;

    if (state.elevation > bestElev) {
      bestX = state.x;
      bestY = state.y;
      bestElev = state.elevation;
    }

    // Check if all restarts done
    if (newRestarts >= opts.maxRestarts) {
      return {
        ...state,
        converged: true,
        convergenceReason: 'restarts_exhausted',
        x: bestX,
        y: bestY,
        elevation: bestElev,
        bestX,
        bestY,
        bestElevation: bestElev,
        restarts: newRestarts,
      };
    }

    // Start new restart from random position
    const newX = Math.random();
    const newY = Math.random();

    return {
      ...state,
      x: newX,
      y: newY,
      elevation: getElev(newX, newY),
      restarts: newRestarts,
      iteration: state.iteration + 1,
      bestX,
      bestY,
      bestElevation: bestElev,
      newRestart: true,
    };
  }

  // Gradient ascent step within current restart
  const stepSize = 0.008;
  const stepX = (grad.dx / magnitude) * stepSize;
  const stepY = (grad.dy / magnitude) * stepSize;

  const newX = clamp(state.x + stepX);
  const newY = clamp(state.y + stepY);
  const newElev = getElev(newX, newY);

  // Update best if improved
  let bestX = state.bestX;
  let bestY = state.bestY;
  let bestElev = state.bestElevation;

  if (newElev > bestElev) {
    bestX = newX;
    bestY = newY;
    bestElev = newElev;
  }

  return {
    ...state,
    x: newX,
    y: newY,
    elevation: newElev,
    iteration: state.iteration + 1,
    bestX,
    bestY,
    bestElevation: bestElev,
    newRestart: false,
  };
}

/**
 * Create initial state for an optimization run.
 *
 * @param {number} x - Starting x coordinate (0-1)
 * @param {number} y - Starting y coordinate (0-1)
 * @param {Function} getElev - Function to get elevation
 * @param {string} algorithm - Algorithm name
 * @returns {Object} Initial state
 */
export function createInitialState(x, y, getElev, algorithm) {
  const elevation = getElev(x, y);

  const baseState = {
    x,
    y,
    elevation,
    iteration: 0,
    converged: false,
    algorithm,
    bestX: x,
    bestY: y,
    bestElevation: elevation,
  };

  // Algorithm-specific initialization
  if (algorithm === 'annealing') {
    return {
      ...baseState,
      temperature: DEFAULTS.simulatedAnnealing.initialTemp,
    };
  }

  if (algorithm === 'random-restart') {
    return {
      ...baseState,
      restarts: 0,
    };
  }

  return baseState;
}

/**
 * Get the step function for a given algorithm name.
 *
 * @param {string} algorithm - Algorithm name
 * @returns {Function} Step function
 */
export function getStepFunction(algorithm) {
  switch (algorithm) {
    case 'gradient':
      return stepGradientAscent;
    case 'newton':
      return stepNewtonRaphson;
    case 'annealing':
      return stepSimulatedAnnealing;
    case 'random-restart':
      return stepRandomRestarts;
    default:
      throw new Error(`Unknown algorithm: ${algorithm}`);
  }
}
