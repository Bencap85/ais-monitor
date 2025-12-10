import { MapContainer, TileLayer, useMap, Marker, Popup, Polygon, GeoJSON, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import React from 'react';
import TileTracker from '../TileTracker.jsx';
import CenterLogger from '../CenterLogger.jsx';
import ShipSocketListener from './ShipSocketListener.jsx';
import Topbar from '../topbar/Topbar.jsx';
import DrawControl from '../DrawControl.jsx';
import FlyToController from '../FlyToController.jsx';
import Loading from '../Loading.jsx';
import ShipPopup from '../../popup/ShipPopup.jsx';
import { useDispatch, useSelector } from 'react-redux';
import { setSelectedShip } from '../../slice/selectedShipSlice.js';
import { setShips } from '../../slice/aisShipsSlice.js';
import { DATA_SOURCES } from '../../constants/constants.js';
import './AisMap.css';
import 'leaflet/dist/leaflet.css';
const { io } = require("socket.io-client");

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

// Get or set unique ID to be sent to API with requests
let clientId = localStorage.getItem("clientId");
if (!clientId) {
    clientId = crypto.randomUUID();
    localStorage.setItem("clientId", clientId);
}

              
export default function AisMap({ mapContext, setIsLoading }) {

    const controllerRef = useRef(null);
    const debounceTimerRef = useRef(null);

    const [shipData, setShipData] = useState([]);
    const [mapReady, setMapReady] = useState(false);
    const selectedShip = useSelector(state => state.selectedShip);
    const visibleTilesRef = useRef([]);
    const startingViewportBounds = useRef(mapContext.current?.viewportBoundsGeojson?.geometry?.coordinates);

    const dispatch = useDispatch();

    const handleTilesChange = (tiles) => {
        const newTilesStr = JSON.stringify(tiles);
        const currentTilesStr = JSON.stringify(visibleTilesRef.current);
        if (newTilesStr !== currentTilesStr) {
            visibleTilesRef.current = tiles;
        }
    }

    const handleAisShipClick = (ship) => {
        if (!ship || !ship.mmsi) {
            return;
        }
        dispatch(setSelectedShip(ship));
    }

    const fetchInitialShips = () => {
        console.log("Received fetch request");
        // Cancel any previous request still in flight
        if (controllerRef.current) {
            console.log("FETCH REQUEST CANCELED");
            controllerRef.current.abort();
        }

        const controller = new AbortController();
        controllerRef.current = controller;
        
        console.log("Fetching...");

        const startTime = performance.now();

        setIsLoading(true);

        fetch(`${API_BASE_URL}/ais/ships-within-bounds`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Client-ID': clientId
            },
            body: JSON.stringify({ geojson: mapContext.current.viewportBoundsGeojson }),
            signal: controller.signal
        })
        .then(response => {
            return response.json();
        })
        .then(data => {

            const endTime = performance.now();
            const elapsed = (endTime - startTime) / 1000; // seconds
            console.log(`Fetch took ${elapsed.toFixed(2)} seconds`);

            console.log("Received initial data from ships-within-bounds");
            console.log("Ship data length was: " + data?.length);

            // Add ships to redux upon receiving API data
            const normalizedShips = data.map((ship) => {
                    return {
                        mmsi: Number(ship.UserID),
                        ...ship
                    }
                }
            );

            // Add selected ship (if available) to results to persist
            // trail across renders even if the selected ship goes out of frame
            if (selectedShip) {
                normalizedShips.push(selectedShip);
            }

            dispatch(setShips(normalizedShips));
            setIsLoading(false);
            
        }).catch(error => {
            if (error.name === "AbortError") {
                console.log("Previous fetch aborted");
            } else {
                console.error("Fetch error:", error);
                setIsLoading(false);
            }
        });
    }

    useEffect(() => {
        fetchInitialShips();
    }, []);

    // Determine if the change in viewport requires a data refetch
    useEffect(() => {
        const observer = setInterval(() => {

            if (viewportHasShifted()) {
                // Debounce: clear any pending timer
                if (debounceTimerRef.current) {
                    clearTimeout(debounceTimerRef.current);
                }

                // Schedule a new fetch after 500ms of no further shifts
                debounceTimerRef.current = setTimeout(() => {
                    fetchInitialShips();
                }, 500);
            }
           
        }, 1000);

        return () => {
            clearInterval(observer);
            if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
            if (controllerRef.current) controllerRef.current.abort();
        };

    }, []);

    function lngDiff(a, b) {
        const diff = Math.abs(a - b);
        return diff > 180 ? 360 - diff : diff;
    }

    const viewportHasShifted = () => {
        const LAT_INDEX = 0
        const LNG_INDEX = 1

        const previousCorners = startingViewportBounds.current[0];
        const currentCorners = mapContext.current?.viewportBoundsGeojson?.geometry?.coordinates[0];
        
        const previousLats = [];
        const previousLngs = [];
        const currentLats = [];
        const currentLngs = [];
        for (let i = 0; i < previousCorners.length && i < currentCorners.length; i++) {
            previousLats.push(previousCorners[i][LAT_INDEX]);
            previousLngs.push(previousCorners[i][LNG_INDEX]);
            currentLats.push(currentCorners[i][LAT_INDEX]);
            currentLngs.push(currentCorners[i][LNG_INDEX]);
        }

        // Find max difference between current and previous lat and 
        // max difference between current and previous longitude
        let maxDiffLat = -1;
        let maxDiffLng = -1;
        let maxDiffLatIndex = -1;
        let maxDiffLngIndex = -1;
        for (let i = 0; i < previousLats.length; i++) {
            const currentDiffLat = Math.abs(previousLats[i] - currentLats[i]);
            const currentDiffLng = Math.abs(previousLngs[i] - currentLngs[i]);

            if (currentDiffLat > maxDiffLat) {
                maxDiffLat = currentDiffLat;
                maxDiffLatIndex = i;
            }
            if (currentDiffLng > maxDiffLng) {
                maxDiffLng = currentDiffLng;
                maxDiffLngIndex = i;
            }
            
        }

        // Convert max differences into % increase of original values
        const previousCornerLat = previousLats[maxDiffLatIndex];
        const previousCornerLng = previousLngs[maxDiffLngIndex];

        const previousLatSpan = Math.abs(Math.max(...previousLats) - Math.min(...previousLats));
        const previousLngSpan = lngDiff(Math.max(...previousLngs), Math.min(...previousLngs));

        const maxIncreaseLat = maxDiffLat / previousLatSpan;
        const maxIncreaseLng = maxDiffLng / previousLngSpan;

        // console.log(`MaxIncreaseLat: ${maxIncreaseLat}`);
        // console.log(`MaxIncreaseLng: ${maxIncreaseLng}`);

        const THRESHOLD_LAT_INCREASE = 0.4;
        const THRESHOLD_LNG_INCREASE = 0.4;

        if (maxIncreaseLat > THRESHOLD_LAT_INCREASE ||
            maxIncreaseLng > THRESHOLD_LNG_INCREASE) {

            startingViewportBounds.current = [currentCorners];
            return true;
        }
        return false;
    }


    const API_KEY = "52kfErgC1p25crhLeyFZ";

    return (
        <div className='map-view-container ais-map-container' >
            <div id='map-container-div'>

                <MapContainer
                    center={[mapContext.current.lat, mapContext.current.lng]}
                    zoom={mapContext.current.zoom}
                    minZoom={4}
                    maxZoom={18}
                    zoomControl={false}
                >
                    <TileTracker onTilesChange={handleTilesChange} />
                    <TileLayer
                        url={`https://api.maptiler.com/maps/dataviz-dark/{z}/{x}/{y}.png?key=${API_KEY}`}
                        attribution='&copy; MapTiler & OpenStreetMap contributors'
                    />
                    <CenterLogger mapContext={mapContext} />
                    <ShipSocketListener
                        visibleTilesRef={visibleTilesRef} 
                        handleAisShipClick={handleAisShipClick}
                        mapContext={mapContext}
                    />

                </MapContainer>
            </div>
        </div>
    )
}