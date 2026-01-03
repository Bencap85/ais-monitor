import './App.css';
import Sidebar from './sidebar/Sidebar.jsx';
import AisMap from './map/ais/AisMap.jsx';
import AisShipPopup from './popup/AisShipPopup.jsx';
import { useState, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setCurrentMode } from './slice/currentModeSlice.js';
import { DATA_SOURCES } from './constants/constants.js';


function App() {

  const [isLoading, setIsLoading] = useState(false);

  const dispatch = useDispatch();
  dispatch(setCurrentMode(DATA_SOURCES.AIS));

  // Initialize map context/bounds
  const mapContext = useRef({
    lat: 36.94,
    lng: -76.3,
    zoom: 10,
    viewportBoundsGeojson: {
      geometry: { "type": "Polygon", "coordinates": [[[-76.89194580385873, 36.608913667193676], [-76.89194580385873, 37.26968150969715], [-75.66971679995248, 37.26968150969715], [-75.66971679995248, 36.608913667193676], [-76.89194580385873, 36.608913667193676]]] }
    }
  });

  // Fetch data from redux store
  const selectedShip = useSelector(state => state.selectedShip);
  const currentMode = useSelector(state => state.currentMode);

  return (
    <div className="App">
      <Sidebar
        isLoading={isLoading}
      />
      {selectedShip && <AisShipPopup ship={selectedShip} />}
      <AisMap
        mapContext={mapContext}
        setIsLoading={setIsLoading} />

    </div>
  );
}

export default App;
