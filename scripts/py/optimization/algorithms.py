"""
Optimization algorithms for finding maxima of objective functions.
Reference implementations matching the JavaScript versions in docs/js/optimization/.

These are used for validation and testing consistency between Python and JS.
"""

import json
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Callable, Tuple, Optional, Dict, Any


@dataclass
class OptimizationConfig:
    """Configuration for optimization algorithms."""
    # Gradient Ascent
    ga_step_size: float = 0.008
    ga_convergence_tol: float = 0.5

    # Newton-Raphson
    nr_convergence_tol: float = 0.3
    nr_damping: float = 0.5
    nr_max_step: float = 0.08
    nr_hessian_threshold: float = -0.1
    nr_fallback_step_size: float = 0.005
    nr_h: float = 0.01  # Finite difference step

    # Simulated Annealing
    sa_initial_temp: float = 1.0
    sa_cooling_rate: float = 0.995
    sa_min_temp: float = 0.01
    sa_step_scale: float = 0.05
    sa_temp_scale: float = 50.0

    # Random Restarts
    rr_max_restarts: int = 5
    rr_max_iter_per_restart: int = 50

    # MCMC (Metropolis-Hastings)
    mcmc_proposal_sd: float = 0.03
    mcmc_log_scale: float = 5.0
    mcmc_use_log_posterior: bool = True


@dataclass
class OptimizationState:
    """State of an optimization run."""
    x: float
    y: float
    elevation: float
    iteration: int = 0
    converged: bool = False
    convergence_reason: Optional[str] = None
    best_x: float = None
    best_y: float = None
    best_elevation: float = None
    temperature: float = 1.0  # For SA
    restarts: int = 0  # For RR
    step_size: float = 0.0
    gradient_magnitude: float = 0.0
    accepted: Optional[bool] = None  # For MCMC

    def __post_init__(self):
        if self.best_x is None:
            self.best_x = self.x
        if self.best_y is None:
            self.best_y = self.y
        if self.best_elevation is None:
            self.best_elevation = self.elevation


class TerrainFunction:
    """Wrapper for terrain data as an objective function."""

    def __init__(self, terrain_data: Dict[str, Any]):
        """
        Initialize with terrain data dict (same format as JSON).

        Args:
            terrain_data: Dict with 'elevations', 'grid', 'stats' keys
        """
        self.elevations = np.array(terrain_data['elevations'])
        self.rows = terrain_data['grid']['rows']
        self.cols = terrain_data['grid']['cols']
        self.stats = terrain_data['stats']

    def __call__(self, x: float, y: float) -> float:
        """Get elevation at normalized coordinates (0-1)."""
        return self.get_elevation(x, y)

    def get_elevation(self, x: float, y: float) -> float:
        """
        Get elevation using bilinear interpolation.

        Args:
            x: Normalized x coordinate (0-1, west to east)
            y: Normalized y coordinate (0-1, south to north)

        Returns:
            Interpolated elevation value
        """
        col = x * (self.cols - 1)
        row = y * (self.rows - 1)

        col0 = max(0, min(int(col), self.cols - 1))
        row0 = max(0, min(int(row), self.rows - 1))
        col1 = min(col0 + 1, self.cols - 1)
        row1 = min(row0 + 1, self.rows - 1)

        dx = col - col0
        dy = row - row0

        v00 = self.elevations[row0, col0]
        v01 = self.elevations[row0, col1]
        v10 = self.elevations[row1, col0]
        v11 = self.elevations[row1, col1]

        elevation = (v00 * (1 - dx) * (1 - dy) +
                     v01 * dx * (1 - dy) +
                     v10 * (1 - dx) * dy +
                     v11 * dx * dy)

        return float(elevation)

    def get_gradient(self, x: float, y: float, h: float = 0.01) -> Tuple[float, float]:
        """Compute gradient using central differences."""
        dx = (self.get_elevation(x + h, y) - self.get_elevation(x - h, y)) / (2 * h)
        dy = (self.get_elevation(x, y + h) - self.get_elevation(x, y - h)) / (2 * h)
        return dx, dy

    def get_hessian_diag(self, x: float, y: float, h: float = 0.01) -> Tuple[float, float]:
        """Compute diagonal elements of Hessian."""
        f = self.get_elevation(x, y)
        fxx = (self.get_elevation(x + h, y) - 2 * f + self.get_elevation(x - h, y)) / (h * h)
        fyy = (self.get_elevation(x, y + h) - 2 * f + self.get_elevation(x, y - h)) / (h * h)
        return fxx, fyy


def clamp(x: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp value to range."""
    return max(min_val, min(max_val, x))


def gradient_magnitude(grad: Tuple[float, float]) -> float:
    """Compute gradient magnitude."""
    return math.sqrt(grad[0] ** 2 + grad[1] ** 2)


def step_gradient_ascent(
    state: OptimizationState,
    terrain: TerrainFunction,
    config: OptimizationConfig = None
) -> OptimizationState:
    """
    Gradient Ascent step.
    Takes a fixed-size step in the direction of steepest ascent.
    """
    if config is None:
        config = OptimizationConfig()

    grad = terrain.get_gradient(state.x, state.y)
    magnitude = gradient_magnitude(grad)

    # Check convergence
    if magnitude < config.ga_convergence_tol:
        state.converged = True
        state.convergence_reason = 'gradient_small'
        return state

    # Normalize step
    step_x = (grad[0] / magnitude) * config.ga_step_size
    step_y = (grad[1] / magnitude) * config.ga_step_size

    new_x = clamp(state.x + step_x)
    new_y = clamp(state.y + step_y)

    state.x = new_x
    state.y = new_y
    state.elevation = terrain(new_x, new_y)
    state.iteration += 1
    state.step_size = config.ga_step_size
    state.gradient_magnitude = magnitude

    # Update best
    if state.elevation > state.best_elevation:
        state.best_x = state.x
        state.best_y = state.y
        state.best_elevation = state.elevation

    return state


def step_newton_raphson(
    state: OptimizationState,
    terrain: TerrainFunction,
    config: OptimizationConfig = None
) -> OptimizationState:
    """
    Newton-Raphson step.
    Uses second derivatives for faster convergence near optima.
    """
    if config is None:
        config = OptimizationConfig()

    h = config.nr_h
    grad = terrain.get_gradient(state.x, state.y, h)
    magnitude = gradient_magnitude(grad)

    # Convergence check
    if magnitude < config.nr_convergence_tol:
        state.converged = True
        state.convergence_reason = 'gradient_small'
        return state

    # Get Hessian
    fxx, fyy = terrain.get_hessian_diag(state.x, state.y, h)

    # Newton step when well-conditioned
    if fxx < config.nr_hessian_threshold:
        step_x = -grad[0] / fxx
    else:
        step_x = grad[0] * config.nr_fallback_step_size

    if fyy < config.nr_hessian_threshold:
        step_y = -grad[1] / fyy
    else:
        step_y = grad[1] * config.nr_fallback_step_size

    # Apply damping
    step_x *= config.nr_damping
    step_y *= config.nr_damping

    # Safety clamp
    step_x = clamp(step_x, -config.nr_max_step, config.nr_max_step)
    step_y = clamp(step_y, -config.nr_max_step, config.nr_max_step)

    new_x = clamp(state.x + step_x)
    new_y = clamp(state.y + step_y)
    actual_step = math.sqrt(step_x ** 2 + step_y ** 2)

    state.x = new_x
    state.y = new_y
    state.elevation = terrain(new_x, new_y)
    state.iteration += 1
    state.step_size = actual_step
    state.gradient_magnitude = magnitude

    # Update best
    if state.elevation > state.best_elevation:
        state.best_x = state.x
        state.best_y = state.y
        state.best_elevation = state.elevation

    return state


def step_simulated_annealing(
    state: OptimizationState,
    terrain: TerrainFunction,
    config: OptimizationConfig = None,
    rng: np.random.Generator = None
) -> OptimizationState:
    """
    Simulated Annealing step.
    Probabilistically accepts worse solutions to escape local optima.
    """
    if config is None:
        config = OptimizationConfig()
    if rng is None:
        rng = np.random.default_rng()

    # Check if cooled
    if state.temperature < config.sa_min_temp:
        state.converged = True
        state.convergence_reason = 'temperature_min'
        state.x = state.best_x
        state.y = state.best_y
        state.elevation = state.best_elevation
        return state

    # Propose random move
    step_size = config.sa_step_scale * state.temperature
    proposed_x = clamp(state.x + (rng.random() - 0.5) * step_size)
    proposed_y = clamp(state.y + (rng.random() - 0.5) * step_size)
    proposed_elev = terrain(proposed_x, proposed_y)

    # Metropolis acceptance
    delta = proposed_elev - state.elevation
    accept_prob = 1.0 if delta > 0 else math.exp(delta / (state.temperature * config.sa_temp_scale))

    if rng.random() < accept_prob:
        state.x = proposed_x
        state.y = proposed_y
        state.elevation = proposed_elev

    # Update best
    if state.elevation > state.best_elevation:
        state.best_x = state.x
        state.best_y = state.y
        state.best_elevation = state.elevation

    # Cool down
    state.temperature *= config.sa_cooling_rate
    state.iteration += 1

    return state


def step_random_restarts(
    state: OptimizationState,
    terrain: TerrainFunction,
    config: OptimizationConfig = None,
    rng: np.random.Generator = None
) -> OptimizationState:
    """
    Random Restarts step.
    Runs gradient ascent from multiple random starting points.
    """
    if config is None:
        config = OptimizationConfig()
    if rng is None:
        rng = np.random.default_rng()

    grad = terrain.get_gradient(state.x, state.y)
    magnitude = gradient_magnitude(grad)
    local_iteration = state.iteration - state.restarts * config.rr_max_iter_per_restart

    # Check if current restart converged
    if magnitude < 0.5 or local_iteration >= config.rr_max_iter_per_restart:
        state.restarts += 1

        # Update best
        if state.elevation > state.best_elevation:
            state.best_x = state.x
            state.best_y = state.y
            state.best_elevation = state.elevation

        # Check if all restarts done
        if state.restarts >= config.rr_max_restarts:
            state.converged = True
            state.convergence_reason = 'restarts_exhausted'
            state.x = state.best_x
            state.y = state.best_y
            state.elevation = state.best_elevation
            return state

        # New random start
        state.x = rng.random()
        state.y = rng.random()
        state.elevation = terrain(state.x, state.y)
        state.iteration += 1
        return state

    # Gradient step
    step_size = 0.008
    step_x = (grad[0] / magnitude) * step_size
    step_y = (grad[1] / magnitude) * step_size

    new_x = clamp(state.x + step_x)
    new_y = clamp(state.y + step_y)

    state.x = new_x
    state.y = new_y
    state.elevation = terrain(new_x, new_y)
    state.iteration += 1

    # Update best
    if state.elevation > state.best_elevation:
        state.best_x = state.x
        state.best_y = state.y
        state.best_elevation = state.elevation

    return state


def step_mcmc(
    state: OptimizationState,
    terrain: TerrainFunction,
    config: OptimizationConfig = None,
    rng: np.random.Generator = None
) -> OptimizationState:
    """
    Single Metropolis-Hastings MCMC step.
    Proposes a new position from a Gaussian centered on current position,
    then accepts/rejects based on the Metropolis criterion.

    Unlike optimization algorithms, MCMC doesn't converge to a point -
    it samples from the posterior distribution proportional to elevation.

    Args:
        state: Current chain state
        terrain: Objective function (elevation as posterior)
        config: Algorithm configuration
        rng: Random number generator

    Returns:
        Updated state with acceptance info
    """
    if config is None:
        config = OptimizationConfig()
    if rng is None:
        rng = np.random.default_rng()

    current_elevation = state.elevation

    # Propose new position using Gaussian random walk
    proposed_x = state.x + rng.standard_normal() * config.mcmc_proposal_sd
    proposed_y = state.y + rng.standard_normal() * config.mcmc_proposal_sd

    # Clamp to valid bounds (slightly inside to avoid edge effects)
    proposed_x = max(0.01, min(0.99, proposed_x))
    proposed_y = max(0.01, min(0.99, proposed_y))

    proposed_elevation = terrain(proposed_x, proposed_y)

    # Compute log acceptance ratio
    if config.mcmc_use_log_posterior:
        # Use log(elevation) as log-posterior for more realistic MCMC behavior
        log_proposal_posterior = math.log(max(1, proposed_elevation))
        log_current_posterior = math.log(max(1, current_elevation))
        log_accept_ratio = (log_proposal_posterior - log_current_posterior) * config.mcmc_log_scale
    else:
        # Direct elevation comparison
        log_accept_ratio = proposed_elevation - current_elevation

    # Metropolis acceptance criterion
    accepted = math.log(rng.random()) < log_accept_ratio

    if accepted:
        state.x = proposed_x
        state.y = proposed_y
        state.elevation = proposed_elevation

    state.iteration += 1
    state.accepted = accepted

    return state


def run_mcmc_chains(
    n_chains: int,
    terrain: TerrainFunction,
    n_iterations: int,
    config: OptimizationConfig = None,
    seed: int = None,
    initial_region: Tuple[float, float, float, float] = (0.1, 0.4, 0.1, 0.4)
) -> Tuple[list, dict]:
    """
    Run multiple MCMC chains from random starting points.

    Args:
        n_chains: Number of parallel chains
        terrain: Objective function
        n_iterations: Number of iterations per chain
        config: Algorithm configuration
        seed: Random seed for reproducibility
        initial_region: (x_min, x_max, y_min, y_max) for starting positions

    Returns:
        Tuple of (chain_histories, summary_stats)
    """
    if config is None:
        config = OptimizationConfig()

    rng = np.random.default_rng(seed)

    x_min, x_max, y_min, y_max = initial_region

    # Initialize chains
    chains = []
    for _ in range(n_chains):
        x0 = x_min + rng.random() * (x_max - x_min)
        y0 = y_min + rng.random() * (y_max - y_min)
        state = OptimizationState(
            x=x0,
            y=y0,
            elevation=terrain(x0, y0)
        )
        chains.append(state)

    # Run chains
    histories = [[] for _ in range(n_chains)]
    total_accepted = 0
    total_proposed = 0

    for _ in range(n_iterations):
        for i, chain in enumerate(chains):
            import copy
            chains[i] = copy.deepcopy(chain)
            chains[i] = step_mcmc(chains[i], terrain, config, rng)
            histories[i].append({
                'x': chains[i].x,
                'y': chains[i].y,
                'elevation': chains[i].elevation,
                'accepted': chains[i].accepted
            })
            if chains[i].accepted:
                total_accepted += 1
            total_proposed += 1

    summary = {
        'n_chains': n_chains,
        'n_iterations': n_iterations,
        'total_accepted': total_accepted,
        'total_proposed': total_proposed,
        'acceptance_rate': total_accepted / total_proposed if total_proposed > 0 else 0,
    }

    return histories, summary


def run_optimization(
    algorithm: str,
    terrain: TerrainFunction,
    x0: float,
    y0: float,
    max_iterations: int = 1000,
    config: OptimizationConfig = None,
    seed: int = None
) -> list:
    """
    Run a complete optimization from start to convergence.

    Args:
        algorithm: One of 'gradient', 'newton', 'annealing', 'random-restart'
        terrain: Terrain objective function
        x0, y0: Starting coordinates
        max_iterations: Maximum iterations before stopping
        config: Algorithm configuration
        seed: Random seed for reproducibility

    Returns:
        List of states (trajectory)
    """
    if config is None:
        config = OptimizationConfig()

    rng = np.random.default_rng(seed)

    # Initialize state
    state = OptimizationState(
        x=x0,
        y=y0,
        elevation=terrain(x0, y0),
        temperature=config.sa_initial_temp,
    )

    trajectory = [state]

    step_fn = {
        'gradient': lambda s: step_gradient_ascent(s, terrain, config),
        'newton': lambda s: step_newton_raphson(s, terrain, config),
        'annealing': lambda s: step_simulated_annealing(s, terrain, config, rng),
        'random-restart': lambda s: step_random_restarts(s, terrain, config, rng),
    }[algorithm]

    while not state.converged and state.iteration < max_iterations:
        # Create a copy for the new state
        import copy
        state = copy.deepcopy(state)
        state = step_fn(state)
        trajectory.append(state)

    return trajectory


def load_terrain(json_path: str) -> TerrainFunction:
    """Load terrain data from JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return TerrainFunction(data)


if __name__ == '__main__':
    # Example usage
    import sys
    from pathlib import Path

    # Find the terrain data
    script_dir = Path(__file__).parent
    terrain_path = script_dir.parent.parent.parent / 'docs' / 'data' / 'arthurs_seat_elevation.json'

    if not terrain_path.exists():
        print(f"Terrain data not found at {terrain_path}")
        sys.exit(1)

    terrain = load_terrain(str(terrain_path))
    print(f"Loaded terrain: {terrain.rows}x{terrain.cols}, elevation {terrain.stats['min']}-{terrain.stats['max']}m")

    # Test each algorithm
    algorithms = ['gradient', 'newton', 'annealing', 'random-restart']
    x0, y0 = 0.25, 0.35  # Start position

    for algo in algorithms:
        trajectory = run_optimization(algo, terrain, x0, y0, max_iterations=500, seed=42)
        final = trajectory[-1]
        print(f"{algo:15s}: {len(trajectory):3d} steps, final={final.elevation:.1f}m at ({final.x:.3f}, {final.y:.3f})")
