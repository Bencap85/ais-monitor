import api.controller.tile_utils as tile_utils
import api.model.model_utils as model_utils
import pipeline

'''
Pipeline steps:

    1. Receive request
        - Need to receive bounds from client

    2. Determine tiles needed to analyze
        - Use tile_utils.get_tile_names(bounds, zoom)
        - zoom will be a predetermined constant. Will need to experiment to dial it in

    3. Fetch and cache tiles (if not cached already)

    4. Detect ships
        - Process all tiles and track detections (the bounding boxes)
        - Filter low-confidence results
        - Merge overlapping detections using NMS

    5. Classify detections
        - For each detection,
            - Slice image inside bounding box
            - Will need to have tile image name saved with each record to do this
            - Classify this image, and assign to ship type

    6. Determine global coordinates for each detection 


    7. Return results to client
        - Return a list of detected_ship objects
        - Should contain global box coordinates, type, confidence, 
'''

sample_geojson = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Norfolk Harbor Section"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-76.330, 36.850],  # Southwest corner
          [-76.330, 36.860],  # Northwest corner
          [-76.310, 36.860],  # Northeast corner
          [-76.310, 36.850],  # Southeast corner
          [-76.330, 36.850]   # Closing the polygon
        ]]
      }
    }
  ]
}

result = pipeline.run_pipeline(sample_geojson)
print("Result*****************************")
print(result)