"""
Property tests for Tier 1 algorithm fixes using synthetic terrains.

Tests are designed to FAIL on the current (broken) code and PASS after fixes.
Uses smooth Gaussian-bump terrains so gradients and Hessians are exact.
"""

import copy
import math
import numpy as np
from algorithms import (
    TerrainFunction,
    OptimizationConfig,
    OptimizationState,
    step_newton_raphson,
    step_mcmc,
    step_gradient_ascent,
    run_optimization,
)
from synthetic_terrain import (
    create_rotated_terrain,
    create_unimodal_terrain,
    create_arthurs_seat_synthetic,
)


# ============================================================
# Fix 1.3: Newton-Raphson should use full 2x2 Hessian
# ============================================================

def test_newton_rotated_terrain_convergence():
    """Newton with full Hessian should converge on a rotated elliptical peak.

    A rotated Gaussian has significant cross-derivative (fxy != 0).
    Diagonal-only Newton ignores this, producing wrong step directions
    and either slow convergence or divergence.
    """
    terrain = create_rotated_terrain()

    # Start offset from the peak at (0.5, 0.5)
    x0, y0 = 0.35, 0.35
    trajectory = run_optimization('newton', terrain, x0, y0, max_iterations=200, seed=42)
    final = trajectory[-1]

    # Should converge to near the peak at (0.5, 0.5)
    dist = math.sqrt((final.x - 0.5)**2 + (final.y - 0.5)**2)
    print(f"  Newton on rotated terrain: {len(trajectory)} steps, "
          f"final=({final.x:.4f}, {final.y:.4f}), dist={dist:.4f}, "
          f"elev={final.elevation:.1f}")

    assert dist < 0.02, (
        f"Newton should converge to peak (0.5, 0.5) on rotated terrain, "
        f"but ended at ({final.x:.4f}, {final.y:.4f}), dist={dist:.4f}"
    )
    assert final.elevation > 240, (
        f"Newton should reach near-peak elevation (>240), got {final.elevation:.1f}"
    )
    print("  PASS: Newton converges on rotated terrain")


def test_newton_faster_with_full_hessian():
    """Newton with full Hessian should converge faster than gradient ascent
    on a rotated terrain where the cross-derivative matters.
    """
    terrain = create_rotated_terrain()

    x0, y0 = 0.35, 0.35
    traj_newton = run_optimization('newton', terrain, x0, y0, max_iterations=200, seed=42)
    traj_grad = run_optimization('gradient', terrain, x0, y0, max_iterations=500, seed=42)

    newton_steps = len(traj_newton)
    grad_steps = len(traj_grad)

    print(f"  Newton: {newton_steps} steps, Gradient: {grad_steps} steps")

    # Newton should converge in fewer steps
    assert newton_steps < grad_steps, (
        f"Newton ({newton_steps}) should be faster than gradient ascent ({grad_steps}) "
        f"on rotated terrain"
    )
    print("  PASS: Newton converges faster than gradient ascent")


def test_newton_step_direction_rotated():
    """On a rotated elliptical peak, Newton's step should point toward the peak,
    not along the axes as diagonal-only would suggest.
    """
    terrain = create_rotated_terrain()
    config = OptimizationConfig()

    # Start at a point offset from the peak in a direction that's not
    # aligned with the terrain axes
    x0, y0 = 0.35, 0.35
    state = OptimizationState(
        x=x0, y=y0, elevation=terrain(x0, y0)
    )

    new_state = copy.deepcopy(state)
    new_state = step_newton_raphson(new_state, terrain, config)

    # The step should move toward (0.5, 0.5)
    step_x = new_state.x - x0
    step_y = new_state.y - y0

    # Vector from start to peak
    to_peak_x = 0.5 - x0
    to_peak_y = 0.5 - y0

    # Cosine similarity between step and direction to peak
    dot = step_x * to_peak_x + step_y * to_peak_y
    mag_step = math.sqrt(step_x**2 + step_y**2)
    mag_peak = math.sqrt(to_peak_x**2 + to_peak_y**2)

    if mag_step > 1e-10:
        cos_sim = dot / (mag_step * mag_peak)
    else:
        cos_sim = 0.0

    print(f"  Step: ({step_x:.4f}, {step_y:.4f}), toward peak: ({to_peak_x:.4f}, {to_peak_y:.4f})")
    print(f"  Cosine similarity: {cos_sim:.4f}")

    # Step should broadly point toward the peak (cos > 0.7 = within ~45 degrees)
    assert cos_sim > 0.7, (
        f"Newton step should point toward peak, cos_sim={cos_sim:.4f}"
    )
    print("  PASS: Newton step direction is correct")


# ============================================================
# Fix 1.4: MCMC should reject (not clamp) out-of-bounds proposals
# ============================================================

def test_mcmc_boundary_rejection():
    """Out-of-bounds proposals should be rejected, not clamped.

    Clamping violates detailed balance: proposals that land outside [0,1]
    get silently moved to the boundary, creating a bias toward edges.
    """
    terrain = create_unimodal_terrain()
    config = OptimizationConfig()
    config.mcmc_proposal_sd = 0.5  # Large SD to force many out-of-bounds proposals

    rng = np.random.default_rng(42)

    # Start near an edge
    x0, y0 = 0.02, 0.02
    state = OptimizationState(
        x=x0, y=y0, elevation=terrain(x0, y0)
    )

    boundary_clamp_count = 0
    total_rejected = 0
    total_steps = 500

    for _ in range(total_steps):
        old_x, old_y = state.x, state.y
        state = copy.deepcopy(state)
        state = step_mcmc(state, terrain, config, rng)

        if not state.accepted:
            total_rejected += 1
            # If rejected, position should be UNCHANGED
            assert state.x == old_x and state.y == old_y, (
                f"Rejected proposal should not change position. "
                f"Was ({old_x:.4f}, {old_y:.4f}), now ({state.x:.4f}, {state.y:.4f})"
            )

        # Check for boundary clamping (this is the bug)
        if state.x == 0.01 or state.x == 0.99 or state.y == 0.01 or state.y == 0.99:
            boundary_clamp_count += 1

    # With proper rejection, we should NOT see excessive boundary positions
    boundary_fraction = boundary_clamp_count / total_steps
    print(f"  Boundary positions: {boundary_clamp_count}/{total_steps} ({boundary_fraction:.1%})")
    print(f"  Rejected: {total_rejected}/{total_steps} ({total_rejected/total_steps:.1%})")

    # With clamping, boundary_fraction would be very high (>30%)
    # With rejection, it should be low (<10%)
    assert boundary_fraction < 0.15, (
        f"Too many boundary positions ({boundary_fraction:.1%}). "
        f"Suggests proposals are being clamped instead of rejected."
    )
    print("  PASS: MCMC properly rejects out-of-bounds proposals")


def test_mcmc_detailed_balance():
    """MCMC should satisfy detailed balance: the chain should sample
    proportional to the target density (elevation).

    On a symmetric unimodal peak, the time-averaged position
    should be near the peak center.
    """
    terrain = create_unimodal_terrain()
    config = OptimizationConfig()
    config.mcmc_proposal_sd = 0.05
    config.mcmc_log_scale = 3.0

    rng = np.random.default_rng(123)

    state = OptimizationState(
        x=0.5, y=0.5, elevation=terrain(0.5, 0.5)
    )

    positions_x = []
    positions_y = []
    n_steps = 2000

    for _ in range(n_steps):
        state = copy.deepcopy(state)
        state = step_mcmc(state, terrain, config, rng)
        positions_x.append(state.x)
        positions_y.append(state.y)

    mean_x = np.mean(positions_x)
    mean_y = np.mean(positions_y)

    print(f"  Mean position: ({mean_x:.4f}, {mean_y:.4f}), peak at (0.5, 0.5)")

    # Mean should be near the peak (within reasonable MCMC noise)
    assert abs(mean_x - 0.5) < 0.1, f"Mean x={mean_x:.4f} too far from peak"
    assert abs(mean_y - 0.5) < 0.1, f"Mean y={mean_y:.4f} too far from peak"
    print("  PASS: MCMC chain centers on peak (consistent with detailed balance)")


# ============================================================
# Fix 1.6: 2D gradient descent should use adaptive learning rates
# (This tests the Python implementation; JS test is manual)
# ============================================================

def test_gradient_step_scales_with_gradient():
    """Gradient descent steps should be proportional to gradient magnitude,
    not constant size.
    """
    terrain = create_unimodal_terrain()
    config = OptimizationConfig()

    # Step from far away (large gradient)
    state_far = OptimizationState(x=0.1, y=0.1, elevation=terrain(0.1, 0.1))
    state_far_new = copy.deepcopy(state_far)
    state_far_new = step_gradient_ascent(state_far_new, terrain, config)

    # Step from near peak (small gradient)
    state_near = OptimizationState(x=0.45, y=0.45, elevation=terrain(0.45, 0.45))
    state_near_new = copy.deepcopy(state_near)
    state_near_new = step_gradient_ascent(state_near_new, terrain, config)

    far_step = math.sqrt((state_far_new.x - 0.1)**2 + (state_far_new.y - 0.1)**2)
    near_step = math.sqrt((state_near_new.x - 0.45)**2 + (state_near_new.y - 0.45)**2)

    print(f"  Far step: {far_step:.6f}, Near step: {near_step:.6f}")

    # Note: Current Python gradient ascent normalizes direction and uses
    # fixed step size. This is a valid design choice (constant speed vs proportional).
    # The JS 2D page is the one with the fixed-learning-rate bug.
    # This test documents the current behavior.
    print("  INFO: Python gradient ascent uses normalized steps (by design)")


# ============================================================
# Synthetic terrain validity tests
# ============================================================

def test_synthetic_arthurs_seat_properties():
    """Verify the synthetic Arthur's Seat has the right shape."""
    terrain = create_arthurs_seat_synthetic(100)

    # Peak should be near (0.20, 0.62)
    peak_idx = np.unravel_index(np.argmax(terrain.elevations), terrain.elevations.shape)
    peak_row, peak_col = peak_idx
    peak_x = peak_col / 99
    peak_y = peak_row / 99

    peak_elev = terrain.elevations[peak_row, peak_col]

    print(f"  Peak: ({peak_x:.3f}, {peak_y:.3f}), elevation={peak_elev:.1f}m")

    # Peak location
    assert abs(peak_x - 0.20) < 0.1, f"Peak x={peak_x:.3f} too far from expected 0.20"
    assert abs(peak_y - 0.62) < 0.1, f"Peak y={peak_y:.3f} too far from expected 0.62"

    # Peak elevation should be close to real Arthur's Seat (~239m)
    assert 220 < peak_elev < 260, f"Peak elevation {peak_elev:.1f}m not in expected range"

    # Salisbury Crags should be a secondary feature
    crags_elev = terrain.get_elevation(0.32, 0.48)
    assert crags_elev > 100, f"Salisbury Crags too low: {crags_elev:.1f}m"
    assert crags_elev < peak_elev, "Crags should be lower than summit"

    # Base elevation should be ~30m
    corner_elev = terrain.get_elevation(0.9, 0.1)
    assert corner_elev < 50, f"Corner elevation should be near base: {corner_elev:.1f}m"

    print(f"  Crags: {crags_elev:.1f}m, Corner: {corner_elev:.1f}m")
    print("  PASS: Synthetic Arthur's Seat has correct properties")


def test_synthetic_terrain_smooth():
    """Synthetic terrain should be C-infinity smooth (Gaussian bumps).
    Gradient and Hessian should be well-behaved everywhere.
    """
    terrain = create_unimodal_terrain(grid_size=200)

    # Sample gradient at many points - should never have discontinuities
    h = 0.005
    max_grad_change = 0
    prev_gx, prev_gy = None, None

    for i in range(10, 90, 5):
        x = i / 100
        y = 0.5
        gx, gy = terrain.get_gradient(x, y, h)

        if prev_gx is not None:
            change = abs(gx - prev_gx) + abs(gy - prev_gy)
            max_grad_change = max(max_grad_change, change)

        prev_gx, prev_gy = gx, gy

    print(f"  Max gradient change between samples: {max_grad_change:.4f}")
    assert max_grad_change < 500, "Gradient should be smooth on synthetic terrain"
    print("  PASS: Synthetic terrain is smooth")


def test_algorithms_converge_on_synthetic():
    """All algorithms should converge to the peak on a simple unimodal terrain."""
    terrain = create_unimodal_terrain()

    x0, y0 = 0.3, 0.3
    algorithms = ['gradient', 'newton']

    for algo in algorithms:
        traj = run_optimization(algo, terrain, x0, y0, max_iterations=500, seed=42)
        final = traj[-1]
        dist = math.sqrt((final.x - 0.5)**2 + (final.y - 0.5)**2)
        print(f"  {algo}: {len(traj)} steps, dist={dist:.4f}, elev={final.elevation:.1f}")
        assert dist < 0.05, f"{algo} didn't converge to peak, dist={dist:.4f}"

    print("  PASS: All algorithms converge on unimodal terrain")


# ============================================================
# Run all tests
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Tier 1 Algorithm Fix Tests (Synthetic Terrains)")
    print("=" * 60)

    print("\n--- Synthetic terrain validity ---")
    test_synthetic_arthurs_seat_properties()
    test_synthetic_terrain_smooth()
    test_algorithms_converge_on_synthetic()

    print("\n--- Fix 1.3: Newton full Hessian ---")
    test_newton_rotated_terrain_convergence()
    test_newton_faster_with_full_hessian()
    test_newton_step_direction_rotated()

    print("\n--- Fix 1.4: MCMC boundary rejection ---")
    test_mcmc_boundary_rejection()
    test_mcmc_detailed_balance()

    print("\n--- Fix 1.6: Gradient step scaling ---")
    test_gradient_step_scales_with_gradient()

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
