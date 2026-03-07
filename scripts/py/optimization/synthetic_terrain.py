"""
Synthetic terrain generators matching docs/js/optimization/synthetic-terrain.js.
Provides smooth (C-infinity) terrains with known properties for testing.
"""

import numpy as np
from algorithms import TerrainFunction


def create_unimodal_terrain(peak_x=0.5, peak_y=0.5, peak_height=250,
                            base_height=50, sigma_x=0.2, sigma_y=0.2,
                            rotation=0, grid_size=100):
    """Generate a single Gaussian bump terrain."""
    cos_r = np.cos(rotation)
    sin_r = np.sin(rotation)

    elevations = np.zeros((grid_size, grid_size))
    for row in range(grid_size):
        y = row / (grid_size - 1)
        for col in range(grid_size):
            x = col / (grid_size - 1)
            dx = x - peak_x
            dy = y - peak_y
            dx_rot = dx * cos_r + dy * sin_r
            dy_rot = -dx * sin_r + dy * cos_r
            exponent = -(dx_rot**2) / (2 * sigma_x**2) - (dy_rot**2) / (2 * sigma_y**2)
            elevations[row, col] = base_height + (peak_height - base_height) * np.exp(exponent)

    return TerrainFunction({
        'elevations': elevations.tolist(),
        'grid': {'rows': grid_size, 'cols': grid_size},
        'stats': {'min': base_height, 'max': peak_height}
    })


def create_rotated_terrain(rotation=np.pi/4):
    """Rotated elliptical peak — Newton with full Hessian should outperform diagonal."""
    return create_unimodal_terrain(
        peak_x=0.5, peak_y=0.5, peak_height=250, base_height=50,
        sigma_x=0.3, sigma_y=0.1, rotation=rotation, grid_size=100
    )


def create_arthurs_seat_synthetic(grid_size=100):
    """
    Smooth synthetic approximation of Arthur's Seat, Edinburgh.

    Captures the main features:
    - Arthur's Seat summit (main peak, ~240m, western side)
    - Salisbury Crags (elongated ridge, ~170m, running NNW-SSE)
    - Broad base elevation of Holyrood Park
    - Steep eastern dropoff
    - Flat low ground to south and east (~30m)

    Returns a C-infinity smooth surface suitable for testing
    optimization algorithms with well-defined gradients and Hessians.
    """
    elevations = np.zeros((grid_size, grid_size))

    # Define Gaussian components
    bumps = [
        # Arthur's Seat summit
        {'cx': 0.20, 'cy': 0.62, 'height': 128, 'sx': 0.06, 'sy': 0.07, 'rot': 0.3},
        # Arthur's Seat shoulder (NE of summit)
        {'cx': 0.25, 'cy': 0.67, 'height': 50, 'sx': 0.07, 'sy': 0.05, 'rot': 0.5},
        # Salisbury Crags ridge
        {'cx': 0.32, 'cy': 0.48, 'height': 80, 'sx': 0.05, 'sy': 0.18, 'rot': 0.2},
        # Broad park base (Holyrood Park general elevation)
        {'cx': 0.25, 'cy': 0.50, 'height': 30, 'sx': 0.20, 'sy': 0.25, 'rot': 0.0},
        # Western slopes
        {'cx': 0.08, 'cy': 0.55, 'height': 15, 'sx': 0.10, 'sy': 0.20, 'rot': 0.0},
    ]

    base_height = 30.0

    for row in range(grid_size):
        y = row / (grid_size - 1)
        for col in range(grid_size):
            x = col / (grid_size - 1)
            z = base_height
            for b in bumps:
                dx = x - b['cx']
                dy = y - b['cy']
                cos_r = np.cos(b['rot'])
                sin_r = np.sin(b['rot'])
                dx_rot = dx * cos_r + dy * sin_r
                dy_rot = -dx * sin_r + dy * cos_r
                exponent = -(dx_rot**2) / (2 * b['sx']**2) - (dy_rot**2) / (2 * b['sy']**2)
                z += b['height'] * np.exp(exponent)
            elevations[row, col] = z

    actual_max = float(elevations.max())

    return TerrainFunction({
        'elevations': elevations.tolist(),
        'grid': {'rows': grid_size, 'cols': grid_size},
        'stats': {'min': base_height, 'max': actual_max}
    })


if __name__ == '__main__':
    # Quick visual check
    terrain = create_arthurs_seat_synthetic(50)
    elev = terrain.elevations

    print(f"Synthetic Arthur's Seat: {terrain.rows}x{terrain.cols}")
    print(f"Elevation range: {elev.min():.1f} - {elev.max():.1f}m")

    peak_idx = np.unravel_index(np.argmax(elev), elev.shape)
    r, c = peak_idx
    print(f"Peak at: row={r}, col={c} ({c/(terrain.cols-1):.3f}, {r/(terrain.rows-1):.3f})")
    print(f"Peak elevation: {elev[r, c]:.1f}m")

    # ASCII map
    print("\nASCII map:")
    for row in range(terrain.rows-1, -1, -5):
        line = f"r{row:2d}: "
        for col in range(0, terrain.cols, 5):
            v = elev[row, col]
            if v > 200: ch = '#'
            elif v > 150: ch = 'X'
            elif v > 100: ch = 'o'
            elif v > 60: ch = '.'
            else: ch = ' '
            line += f'  {ch}'
        print(line)
