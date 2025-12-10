import Ship from "../Ship.jsx";
import "./ShipList.css";

export default function ShipList({ ships, 
                                   setFlyToLocation }) {
    return (
        <div className="ship-list">
            {ships?.map(ship => {
                console.log(JSON.stringify(ship));
                    return <Ship 
                                type={ship.type} 
                                coordinates={ship.coordinates} 
                                confidence={ship.confidence} 
                                estimatedLength={ship.estimatedLength}
                                timestamp={ship.timestamp} 
                                setFlyToLocation={setFlyToLocation}
                                />;
                })}
        </div>
    );
}