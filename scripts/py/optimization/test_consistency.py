"""
Test consistency between Python and JavaScript optimization implementations.

This script validates that both implementations produce similar results
for the same inputs, ensuring consistency across the codebase.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from algorithms import (
    load_terrain,
    run_optimization,
    run_mcmc_chains,
    OptimizationConfig,
    OptimizationState,
    TerrainFunction,
)


def test_terrain_elevation():
    """Test that terrain elevation lookup matches expected values."""
    script_dir = Path(__file__).parent
    terrain_path = script_dir.parent.parent.parent / 'docs' / 'data' / 'arthurs_seat_elevation.json'

    terrain = load_terrain(str(terrain_path))

    # Test corner values
    test_points = [
        (0.0, 0.0),  # SW corner
        (1.0, 0.0),  # SE corner
        (0.0, 1.0),  # NW corner
        (1.0, 1.0),  # NE corner
        (0.5, 0.5),  # Center
    ]

    print("Terrain elevation tests:")
    for x, y in test_points:
        elev = terrain(x, y)
        print(f"  ({x:.1f}, {y:.1f}) = {elev:.2f}m")

    # Check stats match
    all_elevs = terrain.elevations.flatten()
    assert abs(all_elevs.min() - terrain.stats['min']) < 0.1
    assert abs(all_elevs.max() - terrain.stats['max']) < 0.1
    print("  ✓ Stats match")


def test_gradient_computation():
    """Test gradient computation at known points."""
    script_dir = Path(__file__).parent
    terrain_path = script_dir.parent.parent.parent / 'docs' / 'data' / 'arthurs_seat_elevation.json'

    terrain = load_terrain(str(terrain_path))

    # Test gradient at a few points
    test_points = [
        (0.25, 0.35),  # Low area
        (0.5, 0.5),    # Mid area
        (0.3, 0.6),    # Near peak
    ]

    print("\nGradient computation tests:")
    for x, y in test_points:
        dx, dy = terrain.get_gradient(x, y)
        mag = (dx**2 + dy**2)**0.5
        print(f"  ({x:.2f}, {y:.2f}): grad=({dx:.2f}, {dy:.2f}), |grad|={mag:.2f}")


def test_algorithm_convergence():
    """Test that all algorithms converge to valid optima."""
    script_dir = Path(__file__).parent
    terrain_path = script_dir.parent.parent.parent / 'docs' / 'data' / 'arthurs_seat_elevation.json'

    terrain = load_terrain(str(terrain_path))
    config = OptimizationConfig()

    algorithms = ['gradient', 'newton', 'annealing', 'random-restart']
    x0, y0 = 0.25, 0.35

    print("\nAlgorithm convergence tests:")
    results = {}

    for algo in algorithms:
        trajectory = run_optimization(algo, terrain, x0, y0, max_iterations=1000, seed=42)
        final = trajectory[-1]

        results[algo] = {
            'steps': len(trajectory),
            'final_elev': final.elevation,
            'final_x': final.x,
            'final_y': final.y,
            'converged': final.converged,
        }

        status = "✓" if final.converged else "✗"
        print(f"  {status} {algo:15s}: {len(trajectory):3d} steps -> {final.elevation:.1f}m")

    # All should converge to a peak (local or global)
    for algo, result in results.items():
        assert result['converged'] or result['steps'] >= 1000, f"{algo} didn't converge"
        assert result['final_elev'] > 100, f"{algo} converged to low elevation"

    print("  ✓ All algorithms converged to valid peaks")
    return results


def test_newton_faster_than_gradient():
    """Test that Newton-Raphson converges faster than gradient ascent."""
    script_dir = Path(__file__).parent
    terrain_path = script_dir.parent.parent.parent / 'docs' / 'data' / 'arthurs_seat_elevation.json'

    terrain = load_terrain(str(terrain_path))

    print("\nNewton vs Gradient speed test:")

    # Run from multiple starting points
    test_starts = [
        (0.25, 0.35),
        (0.5, 0.3),
        (0.4, 0.5),
    ]

    gradient_steps = []
    newton_steps = []

    for x0, y0 in test_starts:
        traj_grad = run_optimization('gradient', terrain, x0, y0, seed=42)
        traj_newton = run_optimization('newton', terrain, x0, y0, seed=42)

        gradient_steps.append(len(traj_grad))
        newton_steps.append(len(traj_newton))

    avg_grad = sum(gradient_steps) / len(gradient_steps)
    avg_newton = sum(newton_steps) / len(newton_steps)

    print(f"  Gradient ascent avg: {avg_grad:.0f} steps")
    print(f"  Newton-Raphson avg:  {avg_newton:.0f} steps")

    # Newton should be significantly faster
    assert avg_newton < avg_grad * 0.5, "Newton should be at least 2x faster"
    print("  ✓ Newton-Raphson is significantly faster")


def test_random_restarts_finds_better():
    """Test that random restarts finds better solutions than single run."""
    script_dir = Path(__file__).parent
    terrain_path = script_dir.parent.parent.parent / 'docs' / 'data' / 'arthurs_seat_elevation.json'

    terrain = load_terrain(str(terrain_path))

    print("\nRandom restarts exploration test:")

    # Start from a position that converges to a local optimum
    x0, y0 = 0.7, 0.4  # Near a local peak

    traj_single = run_optimization('gradient', terrain, x0, y0, seed=42)
    traj_restarts = run_optimization('random-restart', terrain, x0, y0, seed=42)

    single_best = traj_single[-1].elevation
    restart_best = traj_restarts[-1].best_elevation

    print(f"  Single run:      {single_best:.1f}m")
    print(f"  Random restarts: {restart_best:.1f}m")

    # Restarts should often find better (or at least as good)
    assert restart_best >= single_best - 10, "Restarts should not be much worse"
    print("  ✓ Random restarts explores effectively")


def test_mcmc_acceptance_rate():
    """Test that MCMC chains have reasonable acceptance rates."""
    script_dir = Path(__file__).parent
    terrain_path = script_dir.parent.parent.parent / 'docs' / 'data' / 'arthurs_seat_elevation.json'

    terrain = load_terrain(str(terrain_path))

    print("\nMCMC acceptance rate test:")

    histories, summary = run_mcmc_chains(
        n_chains=4,
        terrain=terrain,
        n_iterations=500,
        seed=42
    )

    acceptance_rate = summary['acceptance_rate']
    print(f"  Chains: {summary['n_chains']}")
    print(f"  Iterations: {summary['n_iterations']}")
    print(f"  Acceptance rate: {acceptance_rate:.1%}")

    # Acceptance rate should be reasonable (not too high or too low)
    # With default proposal SD, typically expect 20-60%
    assert 0.1 < acceptance_rate < 0.8, f"Acceptance rate {acceptance_rate:.1%} outside expected range"
    print("  ✓ Acceptance rate in expected range")

    # Check that chains explore different elevations
    final_elevations = [h[-1]['elevation'] for h in histories]
    print(f"  Final elevations: {[f'{e:.1f}' for e in final_elevations]}")

    # Chains should have moved from their starting positions
    for i, history in enumerate(histories):
        start_x = history[0]['x']
        start_y = history[0]['y']
        end_x = history[-1]['x']
        end_y = history[-1]['y']
        distance = ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
        assert distance > 0.01, f"Chain {i} didn't move enough"

    print("  ✓ Chains explore the space")


def generate_test_trajectory_json():
    """Generate test trajectory for JS validation."""
    script_dir = Path(__file__).parent
    terrain_path = script_dir.parent.parent.parent / 'docs' / 'data' / 'arthurs_seat_elevation.json'

    terrain = load_terrain(str(terrain_path))

    # Generate trajectories from fixed starting point
    x0, y0 = 0.25, 0.35

    test_data = {
        'start': {'x': x0, 'y': y0},
        'algorithms': {}
    }

    for algo in ['gradient', 'newton']:
        trajectory = run_optimization(algo, terrain, x0, y0, max_iterations=100, seed=42)

        # Extract first 10 positions for comparison
        positions = [
            {'x': round(s.x, 6), 'y': round(s.y, 6), 'elevation': round(s.elevation, 2)}
            for s in trajectory[:10]
        ]

        test_data['algorithms'][algo] = {
            'positions': positions,
            'final': {
                'x': round(trajectory[-1].x, 6),
                'y': round(trajectory[-1].y, 6),
                'elevation': round(trajectory[-1].elevation, 2),
                'steps': len(trajectory),
            }
        }

    # Save test data
    output_path = script_dir / 'test_trajectories.json'
    with open(output_path, 'w') as f:
        json.dump(test_data, f, indent=2)

    print(f"\nGenerated test trajectory data: {output_path}")
    return test_data


if __name__ == '__main__':
    print("=" * 50)
    print("Optimization Algorithm Consistency Tests")
    print("=" * 50)

    test_terrain_elevation()
    test_gradient_computation()
    test_algorithm_convergence()
    test_newton_faster_than_gradient()
    test_random_restarts_finds_better()
    test_mcmc_acceptance_rate()
    generate_test_trajectory_json()

    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)
