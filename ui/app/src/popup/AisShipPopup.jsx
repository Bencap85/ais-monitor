import { useDispatch, useSelector } from 'react-redux';
import { useState } from 'react';
import { setSelectedShip } from '../slice/selectedShipSlice.js';
import { getStatus } from '../sidebar/AisShipsListItem.jsx';
import { NAVIGATIONAL_STATUSES, SHIP_STATUSES } from '../constants/constants.js';
import "./AisShipPopup.css";
import PopupHeader from './PopupHeader.jsx';


export default function AisShipPopup({ ship }) {

    const dispatch = useDispatch();

    const [ minimized, setMinimized ] = useState(false);

    const status = getStatus(ship);

    const handleClose = () => {
        dispatch(setSelectedShip(null));
    }

    const handleMinimize = () => {
        setMinimized(!minimized);
    }

    const handleExpand = () => {

    }

    function openBingSearch(query) {
        const encoded = encodeURIComponent(query);
        const url = `https://www.bing.com/search?q=${encoded}`;
        window.open(url, '_blank'); 
    }

    return (
        <div className="ship-popup">

            <PopupHeader
                title={"Selection"}
                handleMinimize={handleMinimize}
                handleExpand={handleExpand}
                handleClose={handleClose}
            />

            { !minimized && (
            <div className="ship-popup-body">
                <div className="header">
                    <h2 className="ship-name">
                        Vessel: {ship?.mmsi}
                    </h2>
                    
                    <div 
                        className="popout-icon-div"
                        onClick={() => openBingSearch(`MMSI ${ship.mmsi}`)}
                        >
                        <div className="popout-icon">
                            ↗
                        </div>
                    </div>

                    <div className="status-wrapper">
                        <div className={status === SHIP_STATUSES.ONLINE 
                                        ? "popup-ship-status online" : "popup-ship-status"}>
                            {status}
                        </div>
                    </div>
                </div>

                <div className="coordinates">
                    [ {ship?.Latitude?.toFixed(4)}, {ship?.Longitude?.toFixed(4)} ]
                </div>

                <div className="ship-popup-grid">
                    <div className="ship-popup-item">
                        <div className="label">MMSI</div>
                        <div className="value">{ship?.mmsi}</div>
                    </div>
                    <div className="ship-popup-item">
                        <div className="label">Heading</div>
                        <div className="value">{ship?.TrueHeading !== 511 ? ship.TrueHeading : "Unknown"}°</div>
                    </div>
                    <div className="ship-popup-item">
                        <div className="label">Navigational Status</div>
                        <div className="value">{NAVIGATIONAL_STATUSES[ship?.NavigationalStatus] || "Unknown"}</div>
                    </div>
                    <div className="ship-popup-item">
                        <div className="label">Speed Over Ground</div>
                        <div className="value">{ship?.Sog} knots</div>
                    </div>
                    
                    <div className="ship-popup-item">
                        <div className="label">Name</div>
                        <div className="value">{ship?.Name || "Unknown"}</div>
                    </div>
                    <div className="ship-popup-item">
                        <div className="label">Type</div>
                        <div className="value">{ship?.ShipTypeName || "Unknown"}</div>
                    </div>
                    <div className="ship-popup-item">
                        <div className="label">Last Update</div>
                        <div className="value">{new Date(ship?.Timestamp).toUTCString()}</div>
                    </div>
                    <div className="ship-popup-item">
                        <div className="label">Length</div>
                        <div className="value">{ship?.ShipLength ? ship?.ShipLength + " meters": "Unknown"}</div>
                    </div>
                </div>
            </div>
            )}
        </div>

    );
}