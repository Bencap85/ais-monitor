

import cv2
import tile_utils
import model_utils
import coordinate_utils
import numpy as np
from ship import Ship
import pipeline_store



TILE_FOLDER = "./tiles" 
TILE_EXTENSION = "webp"

def compute_iou(box1, box2):
    # box format: [x1, y1, x2, y2] = [min_lon, min_lat, max_lon, max_lat]
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area > 0 else 0

def non_max_suppression(ships, iou_threshold=0.5):
    ships = sorted(ships, key=lambda s: s.confidence, reverse=True)
    keep = []
    suppressed = [False] * len(ships)

    for i in range(len(ships)):
        if suppressed[i]:
            continue
        keep.append(ships[i])
        for j in range(i + 1, len(ships)):
            if suppressed[j]:
                continue
            iou = compute_iou(ships[i].bbox, ships[j].bbox)
            if iou > iou_threshold:
                suppressed[j] = True

    return keep

def run_pipeline(geojson_bounds, pipeline_id):

    pipeline_store.update_pipeline_status(pipeline_id, pipeline_store.PipelineStage.FETCHING, 0, 100)

    # Lists all the tiles needed for this run.
    tile_tuples = tile_utils.tiles_within_bounds(geojson_bounds, zoom_levels=[ 15, 16 ] )

    total_tiles = len(tile_tuples)
    current_tile = 0
    pipeline_store.update_pipeline_status(pipeline_id, pipeline_store.PipelineStage.FETCHING, current_tile, total_tiles)

    # Download tiles locally
    for tile_tuple in tile_tuples:
        z, x, y = tile_tuple
        tile_utils.fetch_tile(z, x, y, TILE_FOLDER)
        current_tile += 1
        pipeline_store.update_pipeline_status(pipeline_id, pipeline_store.PipelineStage.FETCHING, current_tile, total_tiles)

    
    pipeline_store.update_pipeline_status(pipeline_id, pipeline_store.PipelineStage.DETECTING, 0, 100)

    # Detect ships per tile
    tile_to_detections = {}
    total_tiles = len(tile_tuples)
    current_tile = 0
    pipeline_store.update_pipeline_status(pipeline_id, pipeline_store.PipelineStage.DETECTING, current_tile, total_tiles)

    for tile_tuple in tile_tuples:
        z, x, y = tile_tuple
        file_name = f"{z}_{x}_{y}.{TILE_EXTENSION}"
        file_path = TILE_FOLDER + "/" + file_name
        image = tile_utils.load_tile_image(file_path)

        detections = model_utils.detect_ships_in_image(image)

        tile_to_detections[tile_tuple] = detections

        current_tile += 1
        pipeline_store.update_pipeline_status(pipeline_id, pipeline_store.PipelineStage.DETECTING, current_tile, total_tiles)


    print(tile_to_detections)

    # Classify detections and save global coordinates to avoid recalculation
    tile_to_ships = {}

    total_tiles = len(tile_tuples)
    current_tile = 0
    pipeline_store.update_pipeline_status(pipeline_id, pipeline_store.PipelineStage.CLASSIFYING, current_tile, total_tiles)

    for tile_tuple in tile_to_detections.keys():
        # The detections within the current tile
        detections = tile_to_detections[tile_tuple]

        z, x, y = tile_tuple
        file_name = f"{z}_{x}_{y}.{TILE_EXTENSION}"
        file_path = TILE_FOLDER + "/" + file_name

        image = tile_utils.load_tile_image(file_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image_resized = cv2.resize(image, (640, 640))

        for detection in detections:
            x_center, y_center, w, h, object_score, class_score = detection
        
            # Convert to corner coordinates
            x1 = int(x_center - w / 2)
            y1 = int(y_center - h / 2)
            x2 = int(x_center + w / 2)
            y2 = int(y_center + h / 2)
        
            # Ensure coordinates are within image bounds
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image_resized.shape[1], x2)
            y2 = min(image_resized.shape[0], y2)
        
            # Crop the detected ship
            ship_crop = image_resized[y1:y2, x1:x2]

            # Classify
            ship_type = model_utils.classify_image(ship_crop)

            # Convert image bounding box coordinates to global coordinates
            lat1, lon1 = coordinate_utils.tile_pixel_to_latlng(z, x, y, x1, y1, 640)
            lat2, lon2 = coordinate_utils.tile_pixel_to_latlng(z, x, y, x2, y2, 640)

            maxLat = max(lat1, lat2)
            minLat = min(lat1, lat2)
            maxLon = max(lon1, lon2)
            minLon = min(lon1, lon2)
            bbox_global = [float(minLon), float(minLat), float(maxLon), float(maxLat)]

            # Convert center coordinates to global coordinates
            lat_center, lon_center = coordinate_utils.tile_pixel_to_latlng(z, x, y, x_center, y_center, 640)
            
            ship = Ship(ship_type, float(object_score), float(lon_center), float(lat_center), bbox_global)
            if tile_tuple not in tile_to_ships:
                tile_to_ships[tile_tuple] = []
            tile_to_ships[tile_tuple].append(ship)

        current_tile += 1
        pipeline_store.update_pipeline_status(pipeline_id, pipeline_store.PipelineStage.CLASSIFYING, current_tile, total_tiles)



    # Use NMS to filter out duplicate detections in global coordinate space
    all_ships = []
    for ships in tile_to_ships.values():
        all_ships.extend(ships)

    filtered_ships = non_max_suppression(all_ships, 0.2)

    # Return results -> convert go GeoJSON
    features = []

    for ship in filtered_ships:

        # Disclude if out-of-bounds
        if not coordinate_utils.is_bbox_within_bounds(ship.bbox, geojson_bounds):
            continue

        # Polygon feature for bounding box
        minLon, minLat, maxLon, maxLat = ship.bbox
        polygon_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [minLon, minLat],
                    [minLon, maxLat],
                    [maxLon, maxLat],
                    [maxLon, minLat],
                    [minLon, minLat]  # Close the loop
                ]]
            },
            "properties": {
                "id": ship.id,
                "type": ship.type,
                "confidence": ship.confidence,
                "coordinates": ship.coordinates,
                "estimatedLength": round(coordinate_utils.longest_bbox_edge(ship.bbox)),
                "source": "bbox"
            }
        }
        features.append(polygon_feature)

    result = {
        "type": "FeatureCollection",
        "features": features
    }

    pipeline_store.set_pipeline_result(pipeline_id, result)    
    pipeline_store.update_pipeline_status(pipeline_id, pipeline_store.PipelineStage.COMPLETED, 1, 1)

    




