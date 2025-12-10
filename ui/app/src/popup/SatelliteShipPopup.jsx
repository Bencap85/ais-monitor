import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setSelectedShip } from '../slice/selectedShipSlice.js';
import { DATA_SOURCES } from '../constants/constants.js';
import { shipTypeToColor } from '../constants/constants.js';
import { useState } from 'react';
import PopupHeader from './PopupHeader.jsx';
// import "./SatelliteShipPopup.css";


export default function SatelliteShipPopup({ type, 
                                    confidence, 
                                    coordinates, 
                                    timestamp,
                                    estimatedLength
                                  }) {

  const dispatch = useDispatch();

  const [ minimized, setMinimized ] = useState(false);
  const [ closed, setClosed ] = useState(false);

  const handleMinimize = () => {
    setMinimized(!minimized);
  }

  const handleExpand = () => {

  }

  const handleClose = () => {
    dispatch(setSelectedShip(null));
    setClosed(!closed);
  }


  return (

      !closed && (

        <div className="ship-popup">
          <PopupHeader 
            title="Selected"
            handleMinimize={handleMinimize}
            handleExpand={handleExpand}
            handleClose={handleClose}
          />

          { !minimized && (
            <div className="ship-popup-body">

            <h2 className="ship-name">
              Ship Type: <span style={{ color: shipTypeToColor[type] }}>{type}</span>
            </h2>

            <div className="coordinates">
              [ {coordinates?.lat?.toFixed(4)}, {coordinates?.lng?.toFixed(4)} ]
            </div>

            <div className="ship-popup-grid">
              <div className="ship-popup-item">
                <div className="label">Confidence</div>
                <div className="value">{Math.round(confidence * 100)}%</div>
              </div>
              <div className="ship-popup-item">
                <div className="label">Estimated Length</div>
                <div className="value">{estimatedLength}m</div>
              </div>
              <div className="ship-popup-item">
                <div className="label">Timestamp</div>
                <div className="value">{new Date(timestamp).toLocaleString()}</div>
              </div>
            </div>
          </div>
          )}
        </div>
      )

  );
}