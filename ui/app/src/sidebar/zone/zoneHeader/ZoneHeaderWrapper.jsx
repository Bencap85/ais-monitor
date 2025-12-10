import ZoneHeader from './ZoneHeader.jsx';
import ZoneSummary from './ZoneSummary.jsx';
import './ZoneHeaderWrapper.css';


export default function ZoneHeaderWrapper({ zone, 
                                            setFlyToLocation, 
                                            expanded, 
                                            handleZoneExpandClick }) {
    return (
        <div className="zone-header-wrapper" onClick={handleZoneExpandClick}>
            <ZoneHeader zone={zone} 
                        setFlyToLocation={setFlyToLocation} 
                        expanded={expanded} />
            { expanded ? <ZoneSummary zone={zone} /> : null }
        </div>
    );
}