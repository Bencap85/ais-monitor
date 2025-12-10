import { useDispatch } from 'react-redux';
import { setSelectedShip } from '../slice/selectedShipSlice.js';
import { shipTypeToColor } from '../constants/constants.js';
import './Ship.css';

export default function Ship({ type, 
                               coordinates, 
                               confidence, 
                               estimatedLength, 
                               timestamp, 
                               setFlyToLocation }) {

    const dispatch = useDispatch();

    const typeToIconPath = {
        "Aircraft Carrier": "aircraft-carrier.png",
        "Military": "military-ship.png",
        "Other Warship": "military-ship.png",
        "Other Ship": "military-ship.png",
        "Cargo": "container-ship.png",
        "Container Ship": "container-ship.png"
    }

    console.log("Coordinates: " + JSON.stringify(coordinates));

    let iconBasePath = "icons/ships/";
    let defaultIconPath = "military-ship.png";
    let typeColor = "";

    function handleClick() {
        const flyParams = {
            lat: coordinates.lat,
            lng: coordinates.lng,
            zoom: 17
        }
        setFlyToLocation(flyParams);
        dispatch(setSelectedShip({ type, 
                          coordinates, 
                          confidence, 
                          estimatedLength, 
                          timestamp }));
    }

    
    const maxLength = 500;
    const percentage = (estimatedLength / maxLength) * 100;

    return (
  <div className="ship-card" onClick={handleClick}>
    <div className="ship-left">
      <div className="ship-icon-wrapper">
        <img
          src={iconBasePath + (typeToIconPath[type]? typeToIconPath[type] : defaultIconPath)}
          alt="Ship Icon"
          className="ship-icon"
        />
      </div>
      <p className="ship-type" style={{ color: shipTypeToColor[type] }}>
        {type}
      </p>
    </div>

    <div className="ship-right">
      <div className="ship-coords ship-data-element">
          <p className="ship-coords">
            [ {coordinates.lat?.toFixed(4)}, {coordinates.lng?.toFixed(4)} ]
          </p>
      </div>
      <div className="length-scale ship-data-element">
        <div className="scale-bar">
            <div className="scale-fill" style={{ width: `${percentage}%` }}></div>
        </div>
      <div className="scale-labels">
          <span>0m</span>
          <span>250m</span>
          <span>500m</span>
      </div>
      {/* <p>Estimated length: {estimatedLength}m</p> */}
      </div>
      <div className="ship-confidence-div ship-data-element">
        <p className="ship-confidence">
            {/* {Math.round(confidence * 100)}% Confidence */}
            .{Math.round(confidence*100)}
        </p>
      </div>
      
    </div>
  </div>
);


}