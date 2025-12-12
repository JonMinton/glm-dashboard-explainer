"""
Generate synthetic Arthur's Seat elevation data.
Uses multiple Gaussian peaks to simulate the real topography.

Real Arthur's Seat features:
- Main summit: 251m at approx 55.9442, -3.1618
- Salisbury Crags ridge: ~150m running NW-SE
- Several smaller peaks and a distinct saddle

This synthetic version captures the key features for optimisation demo.
"""

import json
import math

# Grid dimensions
ROWS = 50
COLS = 50

# Bounding box (same as real Arthur's Seat)
SOUTH = 55.937
NORTH = 55.952
WEST = -3.175
EAST = -3.150

def gaussian_2d(x, y, cx, cy, height, sigma_x, sigma_y, rotation=0):
    """2D Gaussian peak with optional rotation."""
    # Rotate coordinates
    cos_r = math.cos(rotation)
    sin_r = math.sin(rotation)
    dx = x - cx
    dy = y - cy
    x_rot = dx * cos_r + dy * sin_r
    y_rot = -dx * sin_r + dy * cos_r

    return height * math.exp(-(x_rot**2 / (2 * sigma_x**2) + y_rot**2 / (2 * sigma_y**2)))

def generate_elevation(lat, lon):
    """Generate elevation at a given lat/lon based on synthetic peaks."""

    # Normalise coordinates to 0-1 range for easier peak placement
    x = (lon - WEST) / (EAST - WEST)
    y = (lat - SOUTH) / (NORTH - SOUTH)

    elevation = 30  # Base elevation (sea level area)

    # Main summit (Arthur's Seat) - highest peak
    # Real location: 55.9442, -3.1618 -> approx (0.37, 0.47) in normalised coords
    elevation += gaussian_2d(x, y, 0.37, 0.47, 220, 0.12, 0.10)

    # Salisbury Crags - elongated ridge to the northwest
    # Real: runs roughly NW-SE at ~150m
    elevation += gaussian_2d(x, y, 0.25, 0.60, 130, 0.20, 0.06, rotation=0.5)

    # Secondary peak (Crow Hill area)
    elevation += gaussian_2d(x, y, 0.55, 0.35, 90, 0.08, 0.08)

    # Whinny Hill (smaller peak to the east)
    elevation += gaussian_2d(x, y, 0.70, 0.55, 70, 0.10, 0.08)

    # Small bump near Dunsapie Loch
    elevation += gaussian_2d(x, y, 0.60, 0.70, 50, 0.07, 0.07)

    # Lower area (Holyrood Park base)
    elevation += gaussian_2d(x, y, 0.15, 0.25, 40, 0.15, 0.15)

    # Add some texture/noise using multiple small bumps
    elevation += gaussian_2d(x, y, 0.45, 0.30, 30, 0.05, 0.05)
    elevation += gaussian_2d(x, y, 0.30, 0.40, 25, 0.04, 0.04)
    elevation += gaussian_2d(x, y, 0.50, 0.60, 35, 0.06, 0.05)

    return elevation

def main():
    # Generate grid
    lat_step = (NORTH - SOUTH) / (ROWS - 1)
    lon_step = (EAST - WEST) / (COLS - 1)

    elevation_grid = []
    all_elevations = []

    for i in range(ROWS):
        lat = SOUTH + i * lat_step
        row = []
        for j in range(COLS):
            lon = WEST + j * lon_step
            elev = generate_elevation(lat, lon)
            row.append(round(elev, 1))
            all_elevations.append(elev)
        elevation_grid.append(row)

    # Find peaks for reference
    max_elev = max(all_elevations)
    min_elev = min(all_elevations)
    mean_elev = sum(all_elevations) / len(all_elevations)

    # Find the location of the maximum
    max_idx = all_elevations.index(max_elev)
    max_row = max_idx // COLS
    max_col = max_idx % COLS
    max_lat = SOUTH + max_row * lat_step
    max_lon = WEST + max_col * lon_step

    output = {
        'name': "Arthur's Seat (Synthetic)",
        'description': 'Synthetic elevation data mimicking Arthur\'s Seat topography for optimisation visualisation',
        'source': 'Generated using multiple Gaussian peaks',
        'bounds': {
            'south': SOUTH,
            'north': NORTH,
            'west': WEST,
            'east': EAST
        },
        'grid': {
            'rows': ROWS,
            'cols': COLS
        },
        'elevations': elevation_grid,
        'stats': {
            'min': round(min_elev, 1),
            'max': round(max_elev, 1),
            'mean': round(mean_elev, 1)
        },
        'peaks': [
            {'name': 'Main Summit', 'lat': max_lat, 'lon': max_lon, 'elevation': round(max_elev, 1)},
            {'name': 'Salisbury Crags', 'lat': 55.946, 'lon': -3.169, 'elevation': 150},
            {'name': 'Secondary Peak', 'lat': 55.942, 'lon': -3.158, 'elevation': 110}
        ]
    }

    # Save to JSON
    import os
    output_path = '/Users/JonMinton/repos/glm-dashboard-explainer/docs/data/arthurs_seat_elevation.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Saved to {output_path}")
    print(f"Grid size: {ROWS} x {COLS}")
    print(f"Elevation range: {min_elev:.1f}m - {max_elev:.1f}m")
    print(f"Mean elevation: {mean_elev:.1f}m")
    print(f"Global maximum at: ({max_lat:.4f}, {max_lon:.4f})")

if __name__ == '__main__':
    main()
