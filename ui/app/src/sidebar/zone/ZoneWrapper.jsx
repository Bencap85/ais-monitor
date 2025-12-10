import { useState } from 'react';
import ShipList from './ShipList.jsx'
import ZoneHeaderWrapper from './zoneHeader/ZoneHeaderWrapper.jsx';
import Zone from './zoneHeader/ZoneHeader.jsx';
import './ZoneWrapper.css';


export default function ZoneWrapper({ zone, 
                                      setFlyToLocation }) {
    const [ expanded, setExpanded ] = useState(false);

    const handleZoneExpandClick = () => {
        setExpanded(!expanded);
    }

    return (
            <div className="zone-wrapper" >
                <ZoneHeaderWrapper zone={zone} 
                                   setFlyToLocation={setFlyToLocation} 
                                   expanded={expanded}
                                   handleZoneExpandClick={handleZoneExpandClick} />
                {expanded && zone.ships?.length > 0 ? <ShipList ships={zone.ships} 
                                                                setFlyToLocation={setFlyToLocation} /> : null}
        </div>
    );
}
