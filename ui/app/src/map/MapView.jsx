import { MapContainer, TileLayer, useMap, Marker, Popup, Polygon, GeoJSON, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import { useState, useEffect,  } from 'react';
import ReactDOM from 'react-dom';
import React from 'react';
import TileTracker from './TileTracker.jsx';
import ShipPopup from '../popup/SatelliteShipPopup.jsx';
import CenterLogger from './CenterLogger.jsx';
import Topbar from './topbar/Topbar.jsx';
import DrawControl from './DrawControl.jsx';
import FlyToController from './FlyToController.jsx';
import Loading from './Loading.jsx';
import { useDispatch } from 'react-redux';
import { setSelectedShip } from '../slice/selectedShipSlice.js';
import { shipTypeToColor } from '../constants/constants.js';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

const TILE_SERVER_API_KEY = process.env.REACT_APP_TILE_SERVER_API_KEY;
const TILE_SERVER_BASE_URL = process.env.REACT_APP_TILE_SERVER_BASE_URL;

export default function MapView({ 
                                    ships,
                                    toggleShowCreateZoneModal, 
                                    setNewBoundaryGeojson, 
                                    zones, 
                                    flyToLocation,
                                    isLoading,
                                    pipelineStatus,
                                    mapContext }) {

    const dispatch = useDispatch();

    function onZoneCreated(geojson) {
        console.log("New boundary created! geojson: " + JSON.stringify(geojson));
        toggleShowCreateZoneModal();
        setNewBoundaryGeojson(geojson);
    }

    useEffect(() => {
        console.log(zones);
    }, []);

    return (
        <div className='map-view-container'>
            {/* <Topbar /> */}
            
            { isLoading ? <Loading pipelineStatus={pipelineStatus} /> : null }
            <div id='map-container-div'>
                <MapContainer 
                    center={[ mapContext.current.lat, mapContext.current.lng ]} 
                    zoom={mapContext.current.zoom} 
                    zoomControl={false}
                    toggleShowCreateZoneModal={toggleShowCreateZoneModal}
                    >
                    <TileLayer
                        url={`${TILE_SERVER_BASE_URL}/{z}/{x}/{y}.jpg?key=${TILE_SERVER_API_KEY}`}
                    />
                    <CenterLogger mapContext={mapContext} />
                    <DrawControl 
                        onZoneCreated={onZoneCreated} 
                        zones={zones}
                    />
                    <FlyToController flyToLocation={flyToLocation} />
                    {zones.map((zone, i) => 
                        <GeoJSON 
                            key={i}
                            data={zone.shipPositions}
                            style={(feature) => {
                            const type = feature.properties.type;
                            return {
                                color: shipTypeToColor[type],
                                weight: 1,
                                fillOpacity: 0.1
                            };
                            }}
                            onEachFeature={(feature, layer) => {
                            layer.on('click', () => {
                                console.log('Ship clicked:', feature.properties);
                                dispatch(setSelectedShip(feature.properties));
                                
                                });
                            }}
                        />
                    )};
                            
                </MapContainer>
            </div>
        </div>
    );
}
