import { useState } from 'react';
import Ship from '../../Ship.jsx';
import ZoneSummary from './ZoneSummary.jsx';
import "./ZoneHeader.css";

export default function ZoneHeader({ zone, 
                                     setFlyToLocation,
                                     expanded }) {


    return(
        <div className="zone">
            <div className={"zone-header" + (expanded ? " zone-header-expanded" : "")} >
                <p className={"zone-name"}>{zone.name}</p>
                <span className="zone-ship-count">{zone.ships?.length} ship{zone.ships?.length !== 1 ? 's' : ''} detected</span>
                <div className="zone-expand-icon-wrapper">
                    {expanded ? 
                        <img className={"zone-expand-icon"} src="/icons/zone-expand.svg" style={{'transform': 'rotate(90deg)', 'transform-origin': 'center' }}/> : 
                        <img className={"zone-expand-icon"} src="/icons/zone-expand.svg" /> 
                    }
                </div>
            </div> 
            
        </div>
    );
}