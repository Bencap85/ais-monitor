import { useEffect } from 'react';
import { useMap } from 'react-leaflet';

export default function TileTracker({ onTilesChange }) {
  const map = useMap();

  useEffect(() => {
    const updateVisibleTiles = () => {
      const bounds = map.getBounds();
      const fixedZoom = 6;

      const tileSize = 256;
      const nw = map.project(bounds.getNorthWest(), fixedZoom).divideBy(tileSize).floor();
      const se = map.project(bounds.getSouthEast(), fixedZoom).divideBy(tileSize).floor();

      const visibleTiles = [];
      for (let x = nw.x; x <= se.x; x++) {
        for (let y = nw.y; y <= se.y; y++) {
          visibleTiles.push({ x, y, z: fixedZoom });
        }
      }

      onTilesChange(visibleTiles);
    };

    map.on('moveend', updateVisibleTiles);
    updateVisibleTiles(); // initial load

    return () => {
      map.off('moveend', updateVisibleTiles);
    };
  }, [map, onTilesChange]);

  return null;
}

