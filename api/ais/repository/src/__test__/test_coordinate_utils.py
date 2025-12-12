import pytest
from src.coordinate_utils.utils import normalize_lng, normalize_lat, normalize_coordinates

# -----------------------------
# Longitude Tests
# -----------------------------
@pytest.mark.parametrize("lng,expected", [
    (0, 0),
    (180, 180),
    (-180, -180),
    (200, -160),   # wrap
    (-200, 160),   # wrap
    (540, 180),    # multiple wraps
    (-540, -180),  # multiple wraps
])
def test_normalize_lng(lng, expected):
    assert normalize_lng(lng) == expected


# -----------------------------
# Latitude Tests
# -----------------------------
@pytest.mark.parametrize("lat,expected", [
    (0, 0),
    (90, 90),
    (-90, -90),
    (95, 90),      # clamp
    (-95, -90),    # clamp
    (120, 90),     # clamp
    (-120, -90),   # clamp
])
def test_normalize_lat(lat, expected):
    assert normalize_lat(lat) == expected


# -----------------------------
# Polygon Tests
# -----------------------------
def test_normalize_polygon():
    coords = [
        [[-200, 95], [200, -95], [0, 45]]
    ]
    normalized = normalize_coordinates(coords)
    assert normalized == [
        [[160, 90], [-160, -90], [0, 45]]
    ]

