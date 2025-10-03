import math
import os
import requests
import numpy as np
import cv2
import geopandas as gpd
from PIL import Image
from io import BytesIO
from shapely.geometry import box
import coordinate_utils



def compress_to_webp(image: Image) -> None:
    with Image.open(input_path) as img:
        img.save(output_path, format='WEBP', lossless=True)


def latlon_to_tile(lat, lon, zoom):
    """Convert lat/lon to tile x/y at a given zoom level."""
    n = 2 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(math.radians(lat)) + 
              1 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n)
    return x_tile, y_tile

def tile_bounds(x, y, zoom):
    """Get lat/lon bounds of a tile."""
    n = 2 ** zoom
    lon1 = x / n * 360.0 - 180.0
    lat1 = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lon2 = (x + 1) / n * 360.0 - 180.0
    lat2 = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return box(lon1, lat2, lon2, lat1)  # Note: lat2 < lat1

def tiles_within_bounds(geojson: dict, zoom_levels: list) -> list[str]:
    """
    This function returns a list of tile names ( tuple of (z, x, y) ) within geojson bounds at a specified zoom level
    
    Args:
        geojson (dict): GeoJSON object representing the search bounds
        zoom_levels (list): the zoom levels of the search (15 and 16 work well)

    Returns: 
        List of tile names ( tuples of (z, x, y) )
    """
    if geojson["type"] == "Feature":
        geojson = {
            "type": "FeatureCollection",
            "features": [geojson]
        }

    tile_names = []

    for zoom_level in zoom_levels:
        gdf = gpd.GeoDataFrame.from_features(geojson["features"])
        boundary = gdf.geometry.unary_union

        minx, miny, maxx, maxy = boundary.bounds
        x_min, y_max = latlon_to_tile(miny, minx, zoom_level)
        x_max, y_min = latlon_to_tile(maxy, maxx, zoom_level)

        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                tile_poly = tile_bounds(x, y, zoom_level)
                if boundary.intersects(tile_poly):
                    tile_names.append((zoom_level, x, y))

    return tile_names

def fetch_tile(z: int, x: int, y: int, tile_folder: str) -> None:
    """
    Checks if a tile exists locally. If not, fetches it from MapTiler and saves it.
    
    Args:
        z (int): Zoom level
        x (int): Tile x-coordinate
        y (int): Tile y-coordinate
        tile_folder (str): Path to folder where tiles are stored

    Returns:
        str: Full path to the tile image
    """
    tile_name = f"{z}_{x}_{y}.webp"
    tile_path = os.path.join(tile_folder, tile_name)

    # Check if tile already exists
    if os.path.exists(tile_path):
        print(f"Tile {tile_name} exists in cache")
        return

    print(f"Fetching tile {tile_name}...")
    url = f"https://api.maptiler.com/maps/satellite/{z}/{x}/{y}.jpg?key=52kfErgC1p25crhLeyFZ"
    response = requests.get(url)

    if response.status_code == 200:
        # with open(tile_path, "wb") as f:
            # f.write(response.content)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image.save(tile_path, format='WEBP', lossless=True)
        return tile_path
    else:
        raise Exception(f"Failed to fetch tile {z}_{x}_{y}: {str(response.headers)}")

def fetch_tiles(tile_tuples, tile_folder: str) -> None:
    for tile_tuple in tile_tuples:
        z, x, y = tile_tuple
        fetch_tile(z, x, y, tile_folder)

def load_tile_image(file_path: str) -> np.ndarray:
    image = Image.open(file_path)
    return np.array(image)


def get_cropped_tile_from_global_bbox(global_bbox: list, zoom_level: int) -> np.ndarray:
    """
    Returns an image (as np.ndarray) of a global bounding box at a specified zoom level

    Parameters:
        bbox_global (list): [minLon, minLat, maxLon, maxLat]
        zoom_level (int): Zoom level of image

    Returns:
        cropped_image (np.ndarray): Image contained within the provided global bounding box
    """
    pass

# To implement this, will need to:
#
#    1. Determine the tile/s we need (the tiles that this bounding box intersects)
#       - Maybe splice these into 1 image for simplicity
#
#   2. Translate the global coordinates into pixel coordinates of this combined image
#
#   3. Crop the image at those pixel coordinates and return
