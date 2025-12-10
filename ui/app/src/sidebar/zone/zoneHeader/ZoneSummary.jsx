import { useState, useEffect } from 'react';
import './ZoneSummary.css';

export default function ZoneSummary({ zone }) {

    let coordinates = [];
    if (zone?.geojson?.geometry?.coordinates?.[0]) {
        coordinates = zone.geojson.geometry.coordinates[0];
    }

    let hideCoordinates = coordinates.length > 5 ? true : false;
    

      
    return (
        <div className="zone-summary-div">
            <div className="zone-summary-left">
                <p>Type</p>
                <p>Sensitivity</p>
                <p>Area</p>
            </div>
            <div className="zone-summary-right">
                <p>{zone.type}</p>
                <p>{zone.sensitivity}</p>
                <p>61.2 mi²</p>
            </div>
            {/* 
            { hideCoordinates || coordinates.length === 0 ? null : (
            <div className="coordinates-wrapper">
                <p className="zone-summary-property">Coordinates:</p>
                <ul className="coordinates-list">
                    {coordinates?.slice(0, coordinates.length - 1)
                        .map((coord, index) => (
                            <li key={index} className="coordinates-list-element">
                            [ {coord[0]}, {coord[1]} ]
                            </li>
                        ))}
                </ul>
            </div>
            )} */}
            
            
        </div>
    )
}