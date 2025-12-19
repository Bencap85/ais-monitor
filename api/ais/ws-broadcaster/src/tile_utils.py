import math
import logging
from shapely.geometry import shape, box


logger = logging.getLogger(__name__)

def lonlat_to_tile(lon, lat, zoom):
    """Convert lon/lat to tile x/y at a given zoom level."""
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return x_tile, y_tile

def tile_bounds(x, y, zoom):
    """Get the bounding box of a tile in lon/lat."""
    n = 2.0 ** zoom
    lon_deg_min = x / n * 360.0 - 180.0
    lat_rad_max = math.pi * (1 - 2 * y / n)
    lat_deg_max = math.degrees(math.atan(math.sinh(lat_rad_max)))
    lon_deg_max = (x + 1) / n * 360.0 - 180.0
    lat_rad_min = math.pi * (1 - 2 * (y + 1) / n)
    lat_deg_min = math.degrees(math.atan(math.sinh(lat_rad_min)))
    return box(lon_deg_min, lat_deg_min, lon_deg_max, lat_deg_max)

def get_intersecting_tiles(geojson, zoom=6):
    """Return a list of z_x_y tiles intersecting the GeoJSON polygon."""
    polygon = shape(geojson['geometry'])

    # Get bounding box in tile coordinates
    min_lon, min_lat, max_lon, max_lat = polygon.bounds
    x_min, y_max = lonlat_to_tile(min_lon, min_lat, zoom)
    x_max, y_min = lonlat_to_tile(max_lon, max_lat, zoom)

    tiles = []
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            tile_poly = tile_bounds(x, y, zoom)
            if polygon.intersects(tile_poly):
                tiles.append(f"{zoom}_{x}_{y}")
    return tiles

def get_tile_id(lat, lon, zoom=6):
        """Returns the tile id of a point. Used to map ships to its corresponding Websocket update channel."""
        try:
            if lat is None or lon is None:
                raise ValueError("Latitude or longitude is None")
            if not (-85.0511 <= lat <= 85.0511):
                raise ValueError(f"Latitude {lat} out of bounds")
            if not (-180 <= lon <= 180):
                raise ValueError(f"Longitude {lon} out of bounds")
        except Exception as e:
            logger.error(str(e))
            return None
        
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x_tile = int((lon + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
        return f"{zoom}_{x_tile}_{y_tile}"