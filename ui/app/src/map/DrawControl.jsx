import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet-draw';
import { useEffect } from 'react';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import './DrawControl.css';


export default function DrawControl({ onZoneCreated, zones }) {
  const map = useMap();

  const defaultZoneStyle = {
      color: '#FFA500',       // Orange border
            weight: 1,
            fillOpacity: 0.1,  
      pointerEvents: 'none'  
  }

  useEffect(() => {
    if (!map) return;

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Draw zones on map
    for (let zone of zones) {
      console.log("Zone: " + JSON.stringify(zone));
      const layer = L.geoJSON(zone.geojson, {
        style: defaultZoneStyle
    });
      drawnItems.addLayer(layer);
    }

    const drawControl = new L.Control.Draw({
      position: 'topright',
      draw: {
        polygon: {
          shapeOptions: defaultZoneStyle
        },
        rectangle: {
          shapeOptions: defaultZoneStyle
        },
        circle: false,
        marker: false,
        polyline: false,
      }
    });

    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, (e) => {
      const layer = e.layer;
      drawnItems.addLayer(layer);

      const geojson = layer.toGeoJSON();
      onZoneCreated(geojson); // Send data back to parent for saving
    });

    return () => {
      map.removeControl(drawControl);
      map.removeLayer(drawnItems);
    };
  }, [map, onZoneCreated]);

  return null;
};
