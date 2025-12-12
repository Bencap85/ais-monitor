import logging


logger = logging.getLogger(__name__)

def normalize_lng(lng: float) -> float:
    """
    Normalize longitude to the range [-180, 180].
    """
    while lng < -180:
        lng += 360
    while lng > 180:
        lng -= 360
    return lng

def normalize_lat(lat: float) -> float:
    """
    Clamp latitude to the range [-90, 90].
    """
    if lat < -90:
        return -90
    if lat > 90:
        return 90
    return lat

def normalize_coordinates(coords):
    """
    Normalize coordinates for a Polygon.
    Example input: [
        [
            [1.6809082031250002, 50.812877010308966], 
            [1.6809082031250002, 52.855864177853995], 
            [6.569824218750001, 52.855864177853995], 
            [6.569824218750001, 50.812877010308966], 
            [1.6809082031250002, 50.812877010308966]
        ]
    ]
    """
    normalized = []
    for point in coords:
        normalized_point = [[normalize_lng(lng), normalize_lat(lat)] for lng, lat in point]
        normalized.append(normalized_point)
    logger.info(f"Converted original {coords} to normalized {normalized}")
    return normalized
