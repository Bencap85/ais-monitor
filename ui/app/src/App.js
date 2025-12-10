import './App.css';
import MapView from './map/MapView.jsx';
import Sidebar from './sidebar/Sidebar.jsx';
import Topbar from './map/topbar/Topbar.jsx';
import CreateZoneModal from './CreateZoneModal.jsx';
import ShipPopup from './popup/ShipPopup.jsx';
import AisMap from './map/ais/AisMap.jsx';
import { useState, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setSelectedShip } from './slice/selectedShipSlice.js';
import { setCurrentMode } from './slice/currentModeSlice.js';
import { DATA_SOURCES, PIPELINE_STAGES, shipTypeToColor } from "./constants/constants.js";

function App() {

  let visibleTiles = [];
  const [showCreateZoneModal, setShowCreateZoneModal] = useState(false);
  const [newBoundaryGeojson, setNewBoundaryGeojson] = useState(null);
  const [flyToLocation, setFlyToLocation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState(null);

  const mapContext = useRef({
    lat: 36.94,
    lng: -76.3,
    zoom: 10,
    viewportBoundsGeojson: null
  });

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  // Selected Ship from redux store
  const dispatch = useDispatch();
  const selectedShip = useSelector(state => state.selectedShip);
  console.log("Selected Ship: " + JSON.stringify(selectedShip));
  const currentMode = useSelector(state => state.currentMode);
  
  const [ships, setShips] = useState([{
    type: "Cargo",
    coordinates: {
      lat: 36.96,
      lng: -76.36
    },
    confidence: 0.89,
    timestamp: "2025-09-05T11:48:00Z",
    bbox: [0, 0, 0, 0]
  } ]);


  const [zones, setZones] = useState([
    {
      name: "Zone Alpha",
      ships: ships,
      shipGeojson: ""
    }
  ]);
  

  const toggleShowCreateZoneModal = () => {
    setShowCreateZoneModal(!showCreateZoneModal);
  }

  const handleAddZone = (newZone) => {
    
    fetch(`${API_BASE_URL}/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ geojson: newZone.geojson, zoomLevels: newZone.zoomLevels })
    })
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
      })
      .then(data => {
        const pipelineId = data.pipelineId;

        let lastProgress = 0;
        let pollsWithoutUpdate = 1;
        const pollLength = 4; // seconds
        let isFirstPoll = true;

        const pollStatus = () => {
          fetch(`${API_BASE_URL}/${pipelineId}/status`)
            .then(res => res.json())
            .then(status => {
              console.log(`Stage: ${status?.stage}, Progress: ${status?.progress}`);

              // Progress animation below
              if (isFirstPoll) {
                setPipelineStatus({
                  stage: PIPELINE_STAGES[status.stage],
                  progress: status.progress
                });
                setIsLoading(true);
                isFirstPoll = false;
              }


              const targetProgress = status.progress;
              const stage = PIPELINE_STAGES[status.stage];

              if (targetProgress > lastProgress) {
                const steps = 10 * pollsWithoutUpdate;
                const stepSize = (targetProgress - lastProgress) / steps;
                let stepCount = 0;
                let currentProgress = lastProgress;

                const interval = setInterval(() => {
                  stepCount++;
                  currentProgress += stepSize;

                  setPipelineStatus({
                    stage: PIPELINE_STAGES[status.stage],
                    progress: Math.min(currentProgress, targetProgress)
                  });

                  if (stepCount >= steps) {
                    clearInterval(interval);
                    setPipelineStatus({
                      stage: stage,
                      progress: targetProgress
                    });
                  }
                }, (pollLength * 1000) / steps);

                pollsWithoutUpdate = 1;
              } else {
                pollsWithoutUpdate++;
                console.log(`No progress update. Cycles without update: ${pollsWithoutUpdate}`);
              }

              lastProgress = targetProgress;
              // End progress animation

              if (status.stage === "PipelineStage.COMPLETED") {
                fetch(`${API_BASE_URL}/${pipelineId}/result`)
                  .then(res => res.json())
                  .then(result => {
                    const features = result.features;
                    const ships = features.map(feature => ({
                      id: feature.properties.id,
                      type: feature.properties.type,
                      confidence: feature.properties.confidence,
                      coordinates: feature.properties.coordinates,
                      estimatedLength: feature.properties.estimatedLength,
                      bbox: feature.geometry.coordinates
                    }));

                    newZone.ships = ships;
                    newZone.shipPositions = features;
                    setZones([...zones, newZone]);
                    setIsLoading(false);
                  });
              } else {
                // Continue polling after 1 second
                setTimeout(pollStatus, pollLength*1000);
              }
            })
            .catch(err => {
              console.error('Error polling status:', err);
              setIsLoading(false);
            });
        };

        pollStatus(); // Start polling

      })
      .catch(error => {
        console.error('Error during detection:', error);
        setIsLoading(false);
      });

  }

  return (
    <div className="App">
      <Sidebar handleDetectShips={() => { }}
               setFlyToLocation={setFlyToLocation}
               zones={zones} 
               isLoading={isLoading}
               />
      {selectedShip && <ShipPopup ship={selectedShip} />}
      {
        currentMode === DATA_SOURCES.AIS ? (
          <AisMap 
            mapContext={mapContext}
            setIsLoading={setIsLoading} />
        ) : (
          <>
            <MapView
              ships={ships}
              toggleShowCreateZoneModal={toggleShowCreateZoneModal}
              setNewBoundaryGeojson={setNewBoundaryGeojson}
              zones={zones}
              flyToLocation={flyToLocation}
              isLoading={isLoading}
              pipelineStatus={pipelineStatus}
              mapContext={mapContext}
            />
            {newBoundaryGeojson !== null && (
              <CreateZoneModal
                handleAddZone={handleAddZone}
                newBoundaryGeojson={newBoundaryGeojson}
                setNewBoundaryGeojson={setNewBoundaryGeojson}
                numZones={zones.length}
              />
            )}
          </>
        )
      }
    </div>
  );
}

export default App;
