from ultralytics import YOLO
import numpy as np
import cv2
from inference import get_model
from coordinate_utils import tile_pixel_to_latlng
from ship import Ship

# model = YOLO("yolov8n.pt")
model = get_model(model_id="marine-ships-aerial/3", api_key="Jhw7Mm0CWCS3fr256n7C")


def test(file_path):
    print("Model loaded. Resizing image...")
    image = tile_utils.load_tile_image(file_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # ✅ Resize to 640×640
    image_resized = cv2.resize(image, (640, 640))

    # ✅ Normalize and reshape
    input_image = image_resized.astype("float32") / 255.0
    input_image = np.transpose(input_image, (2, 0, 1))         # [C, H, W]
    input_image = np.expand_dims(input_image, axis=0)          # [1, C, H, W]

    print("Running prediction...")
    results = model.predict(input_image)
    pred_array = np.squeeze(results[0])  # Shape: (8400, 6)

    boxes = []
    threshold = 0.5  # Confidence threshold

    print("Filtering results...")
    for pred in pred_array:
        x1, y1, x2, y2, obj_score, class_score = pred
        if obj_score > threshold:
            boxes.append([x1, y1, x2, y2, obj_score])

    for box in boxes:
        print(box)

        image_resized = image
        x_center, y_center, width, height, score = box

        # Convert YOLO format to corner coordinates
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)

        # Draw bounding box
        cv2.rectangle(image_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw center point
        cv2.circle(image_resized, (int(x_center), int(y_center)), radius=2, color=(255, 0, 0), thickness=-1)

        # Add confidence score
        cv2.putText(image_resized, f"{score:.2f}", (x1 + 6, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # 🖼️ Show the image
    cv2.imshow("Ship Detections", cv2.cvtColor(image_resized, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


test("./test_data/25554.jpg")

def detect_ships_in_image(image_path, tile_x, tile_y, tile_z):
    results = model(image_path)
    detections = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            lat, lng = tile_pixel_to_latlng(tile_x, tile_y, tile_z, center_x, center_y)

            ship = Ship(
                ship_type=int(box.cls[0]),
                lat=lat,
                lng=lng,
                bounding_box_coordinates=[x1, y1, x2, y2]
            )
            detections.append(ship)

    return detections