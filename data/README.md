# Data Processing Scripts

Scripts for generating and processing elevation data for the optimisation visualisations.

## Real Elevation Data: OS Terrain 50

OS Terrain 50 provides free 50m resolution elevation data for Great Britain.

### Download Instructions

1. Go to [OS Data Hub - Terrain 50](https://osdatahub.os.uk/downloads/open/Terrain50)

2. Create a free account if you don't have one

3. Download the **NT** tile (covers Edinburgh including Arthur's Seat)
   - Select "ASCII Grid and GML (Grid)" format for easiest processing
   - The download will be a ZIP file containing `.asc` files

4. Extract the ZIP file - you'll find files like:
   - `nt27_OST50GRID_20230517.asc` (or similar date)

### Processing the Data

```bash
cd data/

# Process the downloaded ASCII Grid file
python3 process_os_terrain50.py ~/Downloads/nt/nt27_OST50GRID_*.asc

# Or specify custom output location
python3 process_os_terrain50.py ~/Downloads/nt/nt27_OST50GRID_*.asc --output ../docs/data/arthurs_seat_real.json

# Adjust grid resolution (default is 50x50)
python3 process_os_terrain50.py input.asc --grid-size 100
```

### Script Features

- **Pure Python** for ASCII Grid (.asc) files - no extra dependencies
- **GeoTIFF support** if rasterio is installed (`pip install rasterio`)
- Automatic extraction of Arthur's Seat bounding box
- OSGB36 to WGS84 coordinate conversion
- Bilinear interpolation for resampling

### Arthur's Seat Bounding Box

The script extracts elevation data for this area:
- **OSGB36**: E 327000-329500, N 672000-674500
- **WGS84**: approximately 55.937°N to 55.952°N, 3.175°W to 3.150°W

## Alternative: Synthetic Data

If you can't download real data, the synthetic generator creates plausible terrain:

```bash
python3 generate_arthurs_seat.py
```

This uses multiple Gaussian peaks to approximate Arthur's Seat topography.

## Output Format

Both scripts produce JSON in this format:

```json
{
  "name": "Arthur's Seat, Edinburgh",
  "description": "...",
  "source": "...",
  "bounds": {
    "south": 55.937,
    "north": 55.952,
    "west": -3.175,
    "east": -3.150
  },
  "grid": {
    "rows": 50,
    "cols": 50
  },
  "elevations": [[...], ...],
  "stats": {
    "min": 30.0,
    "max": 251.0,
    "mean": 120.5
  }
}
```

The `elevations` array is row-major order, with row 0 at the southern edge.

## Higher Resolution: Scottish LIDAR

For 2m resolution data:
1. Visit [Scottish Remote Sensing Portal](https://remotesensingdata.gov.scot/data)
2. Search for Edinburgh area
3. Download DTM GeoTIFF files

Note: LIDAR files are much larger and require rasterio to process.
