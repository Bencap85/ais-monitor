import { useMap } from 'react-leaflet';
import { useEffect } from 'react';

export default function FlyToController({ flyToLocation }) {
  const map = useMap();

  useEffect(() => {
    if (flyToLocation) {
      const { lat, lng, zoom } = flyToLocation;
      map.flyTo([lat, lng], zoom || 16, {
        animate: true,
        duration: 0.5
      });
    }
  }, [flyToLocation]);

  return null;
}