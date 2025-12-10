import { NAVIGATIONAL_STATUSES, SHIP_STATUSES } from "../constants/constants";
import { useSelector } from 'react-redux';
// import { selectedShip } from '../slice/selectedShipSlice.js';
import "./AisShipsListItem.css";

export const getStatus = (ship) => {
    let isOnline = false;
    const FIVE_MIN_IN_MS = 5 * 60 * 1000;
    if ((new Date().getTime() - new Date(ship.Timestamp).getTime()) <= FIVE_MIN_IN_MS) {
        isOnline = true;
    }

    return isOnline ? SHIP_STATUSES.ONLINE : SHIP_STATUSES.OFFLINE;
}

export default function AisShipsListItem({ ship, onClick } ) {

    const status = getStatus(ship);

    const selectedShip = useSelector(state => state.selectedShip);

    let className = selectedShip?.mmsi === ship.mmsi
                     ? "ais-ships-list-item selected"
                     : "ais-ships-list-item";


    return (
        <div className={className} onClick={(e) => {
            onClick(ship)
        }} >
            <div className="item-left">
                <div className="title">
                    {ship?.mmsi}
                </div>

                <div className="data-element">
                    <div className="label">
                        Name:
                    </div>
                    <div className="value">
                        {ship.Name || "Unknown"}
                    </div>
                </div>

                <div className="data-element">
                    <div className="label">
                        Status:
                    </div>
                    <div className="value">
                        {NAVIGATIONAL_STATUSES[ship?.NavigationalStatus] || "Unknown"}
                    </div>
                </div>

                <div className="data-element">
                    <div className="label">
                        SOG:
                    </div>
                    <div className="value">
                        {ship?.Sog} knots
                    </div>
                </div>
                {/* [ {ship?.Latitude}, {ship?.Longitude} ] */}
            </div>
            <div className="item-right">
                <div className={status === SHIP_STATUSES.ONLINE 
                                ? "ship-status online" : "ship-status"}>
                    {status}
                </div>
            </div>
        </div>
    );
}