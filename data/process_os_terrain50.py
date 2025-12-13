#!/usr/bin/env python3
"""
Process OS Terrain 50 data for Arthur's Seat visualisation.

This script extracts elevation data from OS Terrain 50 files and converts
it to the JSON format used by the optimisation visualisations.

OS Terrain 50 provides 50m resolution elevation data for Great Britain.
Download from: https://osdatahub.os.uk/downloads/open/Terrain50

For Arthur's Seat, you need tile NT27 (covers Edinburgh area).

Supported formats:
- ASCII Grid (.asc) - can be parsed with pure Python
- GeoTIFF (.tif) - requires rasterio (pip install rasterio)

Usage:
    python process_os_terrain50.py <input_file> [--output <output.json>]

Example:
    python process_os_terrain50.py ~/Downloads/NT27_OST50GRID_20230517.asc
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path

# Arthur's Seat bounding box in OSGB36 (British National Grid) coordinates
# These are approximate eastings/northings for the area of interest
ARTHURS_SEAT_BOUNDS = {
    'min_easting': 327000,   # West
    'max_easting': 329500,   # East
    'min_northing': 672000,  # South
    'max_northing': 674500,  # North
}

# Equivalent lat/lon bounds (for reference in output)
ARTHURS_SEAT_LATLON = {
    'south': 55.937,
    'north': 55.952,
    'west': -3.175,
    'east': -3.150,
}


def osgb_to_latlon(easting, northing):
    """
    Convert OSGB36 British National Grid coordinates to WGS84 lat/lon.

    This is a simplified conversion - for precise work use pyproj.
    Accuracy is ~5m which is fine for visualisation purposes.
    """
    # Helmert transformation parameters (OSGB36 to WGS84)
    # Simplified formulae for central Scotland

    # First convert to lat/lon on Airy ellipsoid
    a = 6377563.396  # Airy semi-major axis
    b = 6356256.909  # Airy semi-minor axis
    F0 = 0.9996012717  # Scale factor on central meridian
    lat0 = math.radians(49)  # Latitude of true origin
    lon0 = math.radians(-2)  # Longitude of true origin
    N0 = -100000  # Northing of true origin
    E0 = 400000   # Easting of true origin

    e2 = 1 - (b*b)/(a*a)
    n = (a-b)/(a+b)
    n2 = n*n
    n3 = n*n*n

    lat = lat0
    M = 0

    # Iteratively solve for latitude
    while True:
        lat = (northing - N0 - M) / (a * F0) + lat

        Ma = (1 + n + (5/4)*n2 + (5/4)*n3) * (lat - lat0)
        Mb = (3*n + 3*n2 + (21/8)*n3) * math.sin(lat - lat0) * math.cos(lat + lat0)
        Mc = ((15/8)*n2 + (15/8)*n3) * math.sin(2*(lat - lat0)) * math.cos(2*(lat + lat0))
        Md = (35/24)*n3 * math.sin(3*(lat - lat0)) * math.cos(3*(lat + lat0))
        M = b * F0 * (Ma - Mb + Mc - Md)

        if abs(northing - N0 - M) < 0.00001:
            break

    cos_lat = math.cos(lat)
    sin_lat = math.sin(lat)
    tan_lat = math.tan(lat)

    nu = a * F0 / math.sqrt(1 - e2 * sin_lat * sin_lat)
    rho = a * F0 * (1 - e2) / pow(1 - e2 * sin_lat * sin_lat, 1.5)
    eta2 = nu / rho - 1

    VII = tan_lat / (2 * rho * nu)
    VIII = tan_lat / (24 * rho * nu**3) * (5 + 3*tan_lat**2 + eta2 - 9*tan_lat**2*eta2)
    IX = tan_lat / (720 * rho * nu**5) * (61 + 90*tan_lat**2 + 45*tan_lat**4)
    X = 1 / (cos_lat * nu)
    XI = 1 / (6 * cos_lat * nu**3) * (nu/rho + 2*tan_lat**2)
    XII = 1 / (120 * cos_lat * nu**5) * (5 + 28*tan_lat**2 + 24*tan_lat**4)

    dE = easting - E0

    lat_rad = lat - VII*dE**2 + VIII*dE**4 - IX*dE**6
    lon_rad = lon0 + X*dE - XI*dE**3 + XII*dE**5

    return math.degrees(lat_rad), math.degrees(lon_rad)


def parse_asc_file(filepath):
    """
    Parse an ESRI ASCII Grid file (.asc).

    Returns:
        dict with keys: ncols, nrows, xllcorner, yllcorner, cellsize, nodata_value, data
    """
    with open(filepath, 'r') as f:
        # Read header - variable number of lines (5 or 6 typically)
        header = {}
        while True:
            pos = f.tell()
            line = f.readline().strip()
            parts = line.split()

            # Check if this looks like a header line (key value pair)
            if len(parts) == 2 and parts[0].replace('_', '').isalpha():
                key = parts[0].lower()
                value = parts[1]
                if key in ('ncols', 'nrows'):
                    header[key] = int(value)
                else:
                    header[key] = float(value)
            else:
                # Not a header line, seek back and break
                f.seek(pos)
                break

        # Set default nodata if not present
        if 'nodata_value' not in header:
            header['nodata_value'] = -9999

        # Read elevation data
        data = []
        for line in f:
            row = [float(v) for v in line.strip().split()]
            data.append(row)

    return header, data


def parse_tif_file(filepath):
    """
    Parse a GeoTIFF file using rasterio.

    Returns:
        dict with keys: ncols, nrows, xllcorner, yllcorner, cellsize, nodata_value, data
    """
    try:
        import rasterio
    except ImportError:
        print("Error: rasterio not installed. Install with: pip install rasterio")
        print("Or use ASCII Grid (.asc) format instead.")
        sys.exit(1)

    with rasterio.open(filepath) as src:
        data = src.read(1)  # Read first band
        transform = src.transform

        header = {
            'ncols': src.width,
            'nrows': src.height,
            'xllcorner': transform.c,  # x coordinate of top-left (we'll adjust)
            'yllcorner': transform.f - src.height * abs(transform.e),  # bottom-left y
            'cellsize': transform.a,  # pixel width (assumes square pixels)
            'nodata_value': src.nodata if src.nodata is not None else -9999
        }

        # Convert to list of lists
        data = data.tolist()

    return header, data


def extract_subset(header, data, bounds):
    """
    Extract a rectangular subset of the grid based on OSGB bounds.

    Returns:
        new_header, new_data
    """
    cellsize = header['cellsize']
    xll = header['xllcorner']
    yll = header['yllcorner']
    ncols = header['ncols']
    nrows = header['nrows']
    nodata = header.get('nodata_value', -9999)

    # Calculate column/row indices for bounds
    col_start = max(0, int((bounds['min_easting'] - xll) / cellsize))
    col_end = min(ncols, int((bounds['max_easting'] - xll) / cellsize) + 1)

    # Note: row 0 is at the TOP of the grid (max northing)
    row_start = max(0, int((yll + nrows * cellsize - bounds['max_northing']) / cellsize))
    row_end = min(nrows, int((yll + nrows * cellsize - bounds['min_northing']) / cellsize) + 1)

    print(f"Extracting subset: rows {row_start}:{row_end}, cols {col_start}:{col_end}")
    print(f"Subset size: {row_end - row_start} rows x {col_end - col_start} cols")

    # Extract subset
    subset_data = []
    for r in range(row_start, row_end):
        row = data[r][col_start:col_end]
        # Replace nodata with 0 (sea level)
        row = [0 if v == nodata or v < 0 else v for v in row]
        subset_data.append(row)

    # Update header for subset
    new_header = {
        'ncols': col_end - col_start,
        'nrows': row_end - row_start,
        'xllcorner': xll + col_start * cellsize,
        'yllcorner': yll + (nrows - row_end) * cellsize,
        'cellsize': cellsize,
    }

    return new_header, subset_data


def resample_grid(data, target_rows, target_cols):
    """
    Resample grid to target size using bilinear interpolation.
    """
    import numpy as np

    data_np = np.array(data)
    src_rows, src_cols = data_np.shape

    # Create output grid
    result = np.zeros((target_rows, target_cols))

    for r in range(target_rows):
        for c in range(target_cols):
            # Map to source coordinates
            src_r = r * (src_rows - 1) / (target_rows - 1)
            src_c = c * (src_cols - 1) / (target_cols - 1)

            # Bilinear interpolation
            r0 = int(src_r)
            r1 = min(r0 + 1, src_rows - 1)
            c0 = int(src_c)
            c1 = min(c0 + 1, src_cols - 1)

            dr = src_r - r0
            dc = src_c - c0

            result[r, c] = (
                data_np[r0, c0] * (1 - dr) * (1 - dc) +
                data_np[r0, c1] * (1 - dr) * dc +
                data_np[r1, c0] * dr * (1 - dc) +
                data_np[r1, c1] * dr * dc
            )

    return result.tolist()


def create_output_json(header, data, output_path):
    """
    Create the JSON output file in the format expected by the visualisations.
    """
    # Calculate lat/lon bounds from OSGB coordinates
    sw_lat, sw_lon = osgb_to_latlon(header['xllcorner'], header['yllcorner'])
    ne_lat, ne_lon = osgb_to_latlon(
        header['xllcorner'] + header['ncols'] * header['cellsize'],
        header['yllcorner'] + header['nrows'] * header['cellsize']
    )

    # Flatten data for stats
    all_elevations = [v for row in data for v in row]

    output = {
        'name': "Arthur's Seat, Edinburgh",
        'description': 'Real elevation data from OS Terrain 50',
        'source': 'Ordnance Survey Terrain 50 (Open Data)',
        'resolution_m': header['cellsize'],
        'bounds': {
            'south': round(sw_lat, 6),
            'north': round(ne_lat, 6),
            'west': round(sw_lon, 6),
            'east': round(ne_lon, 6),
        },
        'osgb_bounds': {
            'min_easting': header['xllcorner'],
            'max_easting': header['xllcorner'] + header['ncols'] * header['cellsize'],
            'min_northing': header['yllcorner'],
            'max_northing': header['yllcorner'] + header['nrows'] * header['cellsize'],
        },
        'grid': {
            'rows': len(data),
            'cols': len(data[0]) if data else 0,
        },
        'elevations': [[round(v, 1) for v in row] for row in data],
        'stats': {
            'min': round(min(all_elevations), 1),
            'max': round(max(all_elevations), 1),
            'mean': round(sum(all_elevations) / len(all_elevations), 1),
        }
    }

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    return output


def main():
    parser = argparse.ArgumentParser(
        description='Process OS Terrain 50 data for Arthur\'s Seat visualisation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process ASCII Grid file
    python process_os_terrain50.py ~/Downloads/nt27_OST50GRID_20230517.asc

    # Process GeoTIFF file (requires rasterio)
    python process_os_terrain50.py ~/Downloads/nt27.tif

    # Specify custom output path
    python process_os_terrain50.py input.asc --output ../docs/data/arthurs_seat_real.json

Download OS Terrain 50 from:
    https://osdatahub.os.uk/downloads/open/Terrain50

For Arthur's Seat, download the NT tile (covers Edinburgh area).
        """
    )

    parser.add_argument('input', help='Input file (.asc or .tif)')
    parser.add_argument('--output', '-o',
                        default='../docs/data/arthurs_seat_elevation.json',
                        help='Output JSON file path')
    parser.add_argument('--grid-size', '-g', type=int, default=50,
                        help='Target grid size (rows and cols, default: 50)')
    parser.add_argument('--bounds', '-b', nargs=4, type=float,
                        metavar=('MIN_E', 'MAX_E', 'MIN_N', 'MAX_N'),
                        help='Custom OSGB bounds (easting/northing)')

    args = parser.parse_args()

    input_path = Path(args.input).expanduser()

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Determine file format
    suffix = input_path.suffix.lower()

    print(f"Reading: {input_path}")

    if suffix == '.asc':
        header, data = parse_asc_file(input_path)
    elif suffix in ('.tif', '.tiff'):
        header, data = parse_tif_file(input_path)
    else:
        print(f"Error: Unsupported file format: {suffix}")
        print("Supported formats: .asc (ASCII Grid), .tif/.tiff (GeoTIFF)")
        sys.exit(1)

    print(f"Full grid: {header['nrows']} rows x {header['ncols']} cols")
    print(f"Cell size: {header['cellsize']}m")
    print(f"Origin: ({header['xllcorner']}, {header['yllcorner']})")

    # Use custom bounds if provided
    bounds = ARTHURS_SEAT_BOUNDS.copy()
    if args.bounds:
        bounds['min_easting'] = args.bounds[0]
        bounds['max_easting'] = args.bounds[1]
        bounds['min_northing'] = args.bounds[2]
        bounds['max_northing'] = args.bounds[3]

    # Extract Arthur's Seat subset
    print(f"\nExtracting Arthur's Seat area...")
    subset_header, subset_data = extract_subset(header, data, bounds)

    # Resample to target grid size if needed
    current_rows = len(subset_data)
    current_cols = len(subset_data[0]) if subset_data else 0

    if current_rows != args.grid_size or current_cols != args.grid_size:
        print(f"Resampling from {current_rows}x{current_cols} to {args.grid_size}x{args.grid_size}...")
        subset_data = resample_grid(subset_data, args.grid_size, args.grid_size)

    # Resolve output path relative to script location
    script_dir = Path(__file__).parent
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = script_dir / output_path

    # Create output JSON
    print(f"\nWriting: {output_path}")
    output = create_output_json(subset_header, subset_data, str(output_path))

    print(f"\nDone!")
    print(f"Grid size: {output['grid']['rows']} x {output['grid']['cols']}")
    print(f"Elevation range: {output['stats']['min']}m - {output['stats']['max']}m")
    print(f"Mean elevation: {output['stats']['mean']}m")
    print(f"Lat/Lon bounds: ({output['bounds']['south']}, {output['bounds']['west']}) to ({output['bounds']['north']}, {output['bounds']['east']})")


if __name__ == '__main__':
    main()
