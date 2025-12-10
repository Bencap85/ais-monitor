import math
from shapely.geometry import shape, box
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.
    Returns distance in meters.
    """
    R = 6371000  # Earth radius in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def longest_bbox_edge(bbox):
    """
    Given a bounding box in [minLon, minLat, maxLon, maxLat] format,
    returns the length in meters of the longest edge.
    """
    minLon, minLat, maxLon, maxLat = bbox

    # Horizontal edge (east-west)
    horizontal = haversine(minLat, minLon, minLat, maxLon)

    # Vertical edge (north-south)
    vertical = haversine(minLat, minLon, maxLat, minLon)

    return max(horizontal, vertical)

# Returns the global Lat, Lng of image pixel coordinates
def tile_pixel_to_latlng(z, x, y, pixel_x, pixel_y, tile_size=256):
    n = 2 ** z
    lon = (x + pixel_x / tile_size) / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (y + pixel_y / tile_size) / n)))
    lat = math.degrees(lat_rad)
    return lat, lon

def is_bbox_within_bounds(bbox: list, geojson: dict) -> bool:
    bounds_polygon = shape(geojson['geometry'])
    detection_box = box(bbox[0], bbox[1], bbox[2], bbox[3])
    return bounds_polygon.intersects(detection_box)


