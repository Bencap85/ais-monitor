class Ship():

    def __init__(self, ship_type, confidence, lng, lat, bbox):
        self.id = f"{ship_type}_{confidence}_{lng}_{lat}"
        self.type = ship_type
        self.confidence = confidence
        self.coordinates = {
            "lat": lat,
            "lng": lng
        }
        # List of form [minLon, minLat, maxLon, maxLat ]
        self.bbox = bbox


    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "confidence": self.confidence,
            "coordinates": self.coordinates,
            "bbox": self.bbox
        }

    def __str__(self):
        return (
        f"Ship\n"
        f"  id: {self.id}\n"
        f"  type: {self.type}\n"
        f"  confidence: {self.confidence}\n"
        f"  coordinates:\n"
        f"    lat: {self.coordinates['lat']}\n"
        f"    lng: {self.coordinates['lng']}\n"
        f"  bbox: {self.bbox}"
    )