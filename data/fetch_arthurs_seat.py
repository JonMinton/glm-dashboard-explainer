"""
Fetch elevation data for Arthur's Seat, Edinburgh using Open-Meteo API.
Generates a grid of elevations suitable for contour visualisation.
"""

import json
import time
import urllib.request
import urllib.parse

# Arthur's Seat bounding box (approximate)
# Centre: 55.9442, -3.1618
# The area is roughly 1.5km x 1.5km
SOUTH = 55.937
NORTH = 55.952
WEST = -3.175
EAST = -3.150

# Grid resolution - 30x30 gives 900 points (fewer API calls)
ROWS = 30
COLS = 30

def fetch_elevations(lats, lons):
    """Fetch elevations for a list of lat/lon pairs from Open-Meteo API."""
    # API accepts up to 100 points per request
    lat_str = ','.join(f'{lat:.6f}' for lat in lats)
    lon_str = ','.join(f'{lon:.6f}' for lon in lons)

    url = f'https://api.open-meteo.com/v1/elevation?latitude={lat_str}&longitude={lon_str}'

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    return data['elevation']

def main():
    # Generate grid points
    lat_step = (NORTH - SOUTH) / (ROWS - 1)
    lon_step = (EAST - WEST) / (COLS - 1)

    all_elevations = []
    all_lats = []
    all_lons = []

    # Create all grid points
    for i in range(ROWS):
        lat = SOUTH + i * lat_step
        for j in range(COLS):
            lon = WEST + j * lon_step
            all_lats.append(lat)
            all_lons.append(lon)

    print(f"Total points to fetch: {len(all_lats)}")
    print(f"Grid size: {ROWS} x {COLS}")
    print(f"Bounding box: ({SOUTH}, {WEST}) to ({NORTH}, {EAST})")

    # Fetch in batches of 100 (API limit)
    batch_size = 100
    elevations = []

    for i in range(0, len(all_lats), batch_size):
        batch_lats = all_lats[i:i+batch_size]
        batch_lons = all_lons[i:i+batch_size]

        print(f"Fetching batch {i//batch_size + 1} of {(len(all_lats) + batch_size - 1)//batch_size}...")

        batch_elevations = fetch_elevations(batch_lats, batch_lons)
        elevations.extend(batch_elevations)

        # Be nice to the API - longer delay to avoid rate limiting
        time.sleep(2)

    # Reshape into 2D grid (row-major order)
    elevation_grid = []
    for i in range(ROWS):
        row = elevations[i*COLS:(i+1)*COLS]
        elevation_grid.append(row)

    # Create output data structure
    output = {
        'name': "Arthur's Seat, Edinburgh",
        'description': 'Elevation data for optimisation visualisation',
        'source': 'Open-Meteo Elevation API (Copernicus DEM GLO-90)',
        'resolution_m': 90,
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
            'min': min(elevations),
            'max': max(elevations),
            'mean': sum(elevations) / len(elevations)
        }
    }

    # Save to JSON
    output_path = '/Users/JonMinton/repos/glm-dashboard-explainer/docs/data/arthurs_seat_elevation.json'

    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to {output_path}")
    print(f"Elevation range: {output['stats']['min']:.1f}m - {output['stats']['max']:.1f}m")
    print(f"Mean elevation: {output['stats']['mean']:.1f}m")

if __name__ == '__main__':
    main()
