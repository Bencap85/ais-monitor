import React, { useState } from 'react';
import './CreateZoneModal.css';

export default function CreateZoneModal({ handleAddZone, newBoundaryGeojson, setNewBoundaryGeojson, numZones }) {
  
    const phoneticMap = {
    0: "Alpha",
    1: "Bravo",
    2: "Charlie",
    3: "Delta",
    4: "Echo",
    5: "Foxtrot",
    6: "Golf",
    7: "Hotel",
    8: "India",
    9: "Juliett",
    10: "Kilo",
    11: "Lima",
    12: "Mike",
    13: "November",
    14: "Oscar",
    15: "Papa",
    16: "Quebec",
    17: "Romeo",
    18: "Sierra",
    19: "Tango",
    20: "Uniform",
    21: "Victor",
    22: "Whiskey",
    23: "X-ray",
    24: "Yankee",
    25: "Zulu"
  };
  
  const [errorMessage, setErrorMessage] = useState("");
  const [zoneName, setZoneName] = useState('Zone ' + phoneticMap[numZones % 25]);
  const [zoneType, setZoneType] = useState('Military');
  const [sensitivity, setSensitivity] = useState('Moderate');
  const [currentZoomLevel, setCurrentZoomLevel] = useState(15);
  const [zoomLevels, setZoomLevels] = useState([]);
  const [notes, setNotes] = useState('');
  const [autoClassify, setAutoClassify] = useState(true);

  // When a boundary is created, calls handleSubmit
  const handleSubmit = () => {
    const newZone = {
        name: zoneName,
        type: zoneType,
        sensitivity: sensitivity,
        zoomLevels: zoomLevels,
        notes: notes,
        autoClassify: autoClassify,
        geojson: newBoundaryGeojson,
        ships: []
    }

    let errorMessage = validateForm(newZone);

    if (errorMessage !== "") {
      setErrorMessage(errorMessage);
      return;
    }

    handleAddZone(newZone);
    setNewBoundaryGeojson(null);
    
  };

  const validateForm = (formData) => {
    
    if (formData.zoomLevels.length < 1) {
      return "No zoom level provided";
    }
    return "";
  }

  const handleCancelClick = () => {
    setNewBoundaryGeojson(null);
  }

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        {errorMessage !== "" && 
          <div className="error-message-wrapper" style={{ color: 'red' }}>{errorMessage}</div>
        }
        <h2>Create New Zone</h2>

        <label>Zone Name</label>
        <input
          type="text"
          value={zoneName}
          onChange={(e) => setZoneName(e.target.value)}
        />

        <label>Zone Type</label>
        <select value={zoneType} onChange={(e) => setZoneType(e.target.value)}>
          <option>Military</option>
          <option>Cargo</option>
          <option>Fishing</option>
          <option>Surveillance</option>
        </select>

        <label>Sensitivity</label>
        <select value={sensitivity} onChange={(e) => setSensitivity(e.target.value)}>
          <option>Low</option>
          <option>Moderate</option>
          <option>High</option>
          <option>Critical</option>
        </select>

        <label>Intel Notes</label>
        <textarea
          rows="3"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />

        <div className="zoom-levels-wrapper">
          <div className="zoom-levels">
            <label>Zoom Levels: {zoomLevels.map(level => {
                return <p className="zoom-level">{level}, </p>
              })}
            </label>
          </div>

          <input
            type="text"
            value={currentZoomLevel}
            onChange={(e) => {
              let zoomLevelValue = e.target.value === '' ? 0 : parseInt(e.target.value);
              setCurrentZoomLevel(zoomLevelValue);
            }}
          />
          
          <button className="add-zoom-level-button" onClick={() => {
            setZoomLevels([...zoomLevels, currentZoomLevel]);
            setCurrentZoomLevel(15);
          }} >Add zoom level</button>

          <button className="remove-zoom-levels-button" style={{ float: "right", marginRight: "0" }} onClick={() => {
            setZoomLevels([]);
            setCurrentZoomLevel(15);
          }} >Remove zoom levels</button>
        </div>

        <div className="modal-actions">
          <button className="create-zone-button" onClick={handleSubmit}>Create zone</button>
          <button className="cancel-zone-button"onClick={handleCancelClick}>Cancel</button>
        </div>
      </div>
    </div>
  );
}