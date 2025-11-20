from ultralytics import YOLO
from inference import get_model
import numpy as np
import cv2
import matplotlib.pyplot as plt
from coordinate_utils import tile_pixel_to_latlng
import tile_utils as tile_utils
from domain.ship import Ship

detection_model = None
classification_model = None

def load_models():
    global detection_model, classification_model
    detection_model = get_model(model_id="marine-ships-aerial/3", api_key="Jhw7Mm0CWCS3fr256n7C")
    classification_model = get_model(model_id="ship-classification/1", api_key="Jhw7Mm0CWCS3fr256n7C")
    print("Models loaded successfully")


def filter_predictions(predictions, confidence_threshold=0.5):
    filtered_predictions = []
    for prediction in predictions:
        x, y, w, h, o, c = prediction
        if o > confidence_threshold:
            filtered_predictions.append(prediction)

    return filtered_predictions
        

def merge_boxes(boxes, iou_threshold=0.4):
    """
    Applies Non-Maximum Suppression (NMS) to a list of YOLO-format boxes with actual image coordinates.

    Args:
        boxes (list): List of [x_center, y_center, width, height, object_score, class_score]
        iou_threshold (float): IOU threshold for merging overlapping boxes.

    Returns:
        List of merged boxes in the same format: [x_center, y_center, width, height, object_score, class_score]
    """
    if not boxes:
        return []

    boxes_for_nms = []
    scores = []

    for box in boxes:
        x_center, y_center, w, h, object_score, class_score = box
        x = x_center - w / 2
        y = y_center - h / 2
        boxes_for_nms.append([int(x), int(y), int(w), int(h)])
        scores.append(float(object_score))

    # Apply NMS
    indices = cv2.dnn.NMSBoxes(boxes_for_nms, scores, score_threshold=0.0, nms_threshold=iou_threshold)

    # Return original-format boxes that survived NMS
    merged = [boxes[i] for i in indices.flatten()]
    return merged


def detect_ships_in_image(image: np.ndarray) -> list:
    '''
    Receives image, returns a list of detections as boxes. Appends file_path to each detection for reference
    '''
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize to 640×640
    image_resized = cv2.resize(image, (640, 640))

    # Normalize and reshape
    input_image = image_resized.astype("float32") / 255.0
    input_image = np.transpose(input_image, (2, 0, 1))         # [C, H, W]
    input_image = np.expand_dims(input_image, axis=0)          # [1, C, H, W]

    print("Running prediction...")
    results = detection_model.predict(input_image)

    predictions = np.squeeze(results[0])  # Shape: (8400, 6)


    # Filter predictions
    filtered_predictions = filter_predictions(predictions, 0.5)

    # Display predictions

    
    # Merge boxes
    merged_boxes = merge_boxes(filtered_predictions)

    return merged_boxes

def classify_image(ship_image: np.ndarray) -> str:
    """
    Classifies an image as a ship type (battleship, container, etc). Accepts a cropped image as input,
    and performs image transformations to prepare it for the classification model.

    Args:
        image (np.ndarray): The cropped image we are classifying

    Returns: The classification as a str
    """
    # Resize to classification model input size (e.g., 224×224)
    ship_resized = cv2.resize(ship_image, (224, 224))
    ship_input = ship_resized.astype("float32") / 255.0
    ship_input = np.transpose(ship_input, (2, 0, 1))  # [C, H, W]
    ship_input = np.expand_dims(ship_input, axis=0)   # [1, C, H, W]

    # Run classification
    class_result = classification_model.predict(ship_input)
    class_probs = np.squeeze(class_result[0])
    class_id = int(np.argmax(class_probs))
    class_conf = float(class_probs[class_id])
    class_name = classification_model.class_names[class_id]

    return class_name



def non_max_suppression(ships, iou_threshold=0.5):
    """
    Uses Non Max Suppression in global coordinate space to filter out duplicate detections.

    Developed specifically for filtering duplicate detections of the same ships caused by 
    running detections over the same area at more than 1 zoom level.
    """
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

def filter_unwanted_classes(ships: list[Ship]) -> list[Ship]:
    """
    Filters out unwanted ships by their classification
    """

    unwanted = [ 'Dock', 'Landing']
    filtered_ships = []
    for ship in ships:
        if ship.type not in unwanted:
            filtered_ships.append(ship)

    return filtered_ships

