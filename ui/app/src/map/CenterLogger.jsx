import { useMap, useMapEvents } from 'react-leaflet';
import { useEffect, useState } from 'react';
import './CenterLogger.css';

export default function CenterLogger({ mapContext }) {
  const [center, setCenter] = useState({ lat: 0, lng: 0 });

  useMapEvents({
    move: (e) => {
      const map = e.target;
      const newCenter = map.getCenter();
      const zoom = map.getZoom();

      const determineViewportGeojson = (mapInstance) => {
          const bounds = mapInstance.getBounds();
          const northWest = bounds.getNorthWest();
          const northEast = bounds.getNorthEast();
          const southEast = bounds.getSouthEast();
          const southWest = bounds.getSouthWest();

          const geojson = {
              type: "Feature",
              properties: {},
              geometry: {
              type: "Polygon",
              coordinates: [[
                  [southWest.lng, southWest.lat],
                  [northWest.lng, northWest.lat],
                  [northEast.lng, northEast.lat],
                  [southEast.lng, southEast.lat],
                  [southWest.lng, southWest.lat] 
              ]]
              }
          };
        return geojson;
      }

      const viewportBoundsGeojson = determineViewportGeojson(map);
      
      mapContext.current = {
        lat: newCenter.lat, 
        lng: newCenter.lng,
        zoom:  zoom,
        viewportBoundsGeojson: viewportBoundsGeojson
      };
      setCenter({ lat: newCenter.lat, lng: newCenter.lng });
    }
  });

  return (
    <div className="center-logger" >
      {center.lat.toFixed(5)}, {center.lng.toFixed(5)}
    </div>
  );
}
