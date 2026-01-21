import { MapContainer, TileLayer } from 'react-leaflet';
import { useState, useEffect, useRef } from 'react';
import React from 'react';
import TileTracker from '../TileTracker.jsx';
import CenterLogger from '../CenterLogger.jsx';
import ShipSocketListener from './ShipSocketListener.jsx';
import ShipMarkerDrawer from './ShipMarkerDrawer.jsx';
import { useDispatch, useSelector } from 'react-redux';
import { setSelectedShip } from '../../slice/selectedShipSlice.js';
import { setShips } from '../../slice/aisShipsSlice.js';
import './AisMap.css';
import 'leaflet/dist/leaflet.css';

const REPOSITORY_SERVICE_BASE_URL = process.env.REACT_APP_REPOSITORY_SERVICE_BASE_URL;
const MAPBOX_API_KEY = process.env.REACT_APP_MAPBOX_API_KEY;

// Get or set unique ID to be sent to API with requests
let clientId = localStorage.getItem("clientId");
if (!clientId) {
    clientId = crypto.randomUUID();
    clientId = 1000;
    localStorage.setItem("clientId", clientId);
}
              
export default function AisMap({ mapContext, setIsLoading }) {

    const controllerRef = useRef(null);
    const debounceTimerRef = useRef(null);

    const selectedShip = useSelector(state => state.selectedShip);
    const visibleTilesRef = useRef([]);
    const startingViewportBounds = useRef(mapContext.current.viewportBoundsGeojson.geometry.coordinates);

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

        const fetchStartTime = performance.now();

        setIsLoading(true);

        const twentyFourHoursAgoUtc = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
        const startTime = twentyFourHoursAgoUtc;
        const endTime = new Date().toISOString();

        fetch(`${REPOSITORY_SERVICE_BASE_URL}/ships-within-bounds`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Client-ID': clientId
            },
            body: JSON.stringify({ 
                geojson: mapContext.current.viewportBoundsGeojson,
                startTime,
                endTime
            }),
            signal: controller.signal
        })
        .then(response => {
            return response.json();
        })
        .then(data => {

            const fetchEndTime = performance.now();
            const elapsed = (fetchEndTime - fetchStartTime) / 1000; // seconds
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

    function getLngSpan(lngs) {
        // Normalize to [-180, 180]
        const normalized = lngs.map(l => ((l + 180) % 360 + 360) % 360 - 180);
        normalized.sort((a, b) => a - b);

        const diffs = [];
        for (let i = 0; i < normalized.length - 1; i++) {
            diffs.push(normalized[i + 1] - normalized[i]);
        }
        // Add wrap-around difference
        diffs.push(360 - (normalized[normalized.length - 1] - normalized[0]));

        // The span is the complement of the largest gap
        const maxGap = Math.max(...diffs);
        return 360 - maxGap;
    }

    const viewportHasShifted = () => {
        const LNG_INDEX = 0;
        const LAT_INDEX = 1;

        const previousCorners = startingViewportBounds.current[0];
        const currentCorners = mapContext.current?.viewportBoundsGeojson?.geometry?.coordinates[0];

        const previousLats = previousCorners.map(c => c[LAT_INDEX]);
        const previousLngs = previousCorners.map(c => c[LNG_INDEX]);
        const currentLats = currentCorners.map(c => c[LAT_INDEX]);
        const currentLngs = currentCorners.map(c => c[LNG_INDEX]);

        let maxDiffLat = 0;
        let maxDiffLng = 0;
        for (let i = 0; i < previousCorners.length; i++) {
            maxDiffLat = Math.max(maxDiffLat, Math.abs(previousLats[i] - currentLats[i]));
            maxDiffLng = Math.max(maxDiffLng, lngDiff(previousLngs[i], currentLngs[i]));
        }

        const previousLatSpan = Math.abs(Math.max(...previousLats) - Math.min(...previousLats));
        const previousLngSpan = getLngSpan(previousLngs);

        const maxIncreaseLat = maxDiffLat / previousLatSpan;
        const maxIncreaseLng = maxDiffLng / previousLngSpan;

        const THRESHOLD_LAT_INCREASE = 0.4;
        const THRESHOLD_LNG_INCREASE = 0.4;

        if (maxIncreaseLat > THRESHOLD_LAT_INCREASE || maxIncreaseLng > THRESHOLD_LNG_INCREASE) {
            startingViewportBounds.current = [currentCorners];
            return true;
        }
        return false;
    };

    return (
        <div className='map-view-container ais-map-container' >
            <div id='map-container-div'>

                <MapContainer
                    center={[mapContext.current.lat, mapContext.current.lng]}
                    zoom={mapContext.current.zoom}
                    minZoom={4}
                    maxZoom={18}
                    zoomControl={false}
                    worldCopyJump={true}
                >
                    <TileTracker onTilesChange={handleTilesChange} />
                    <TileLayer
                        url={`https://api.maptiler.com/maps/dataviz-dark/{z}/{x}/{y}.png?key=${MAPBOX_API_KEY}`}
                        attribution='&copy; MapTiler & OpenStreetMap contributors'
                    />
                    <CenterLogger mapContext={mapContext} />
                    <ShipSocketListener
                        visibleTilesRef={visibleTilesRef} 
                        handleAisShipClick={handleAisShipClick}
                        mapContext={mapContext}
                    />
                    <ShipMarkerDrawer 
                        handleAisShipClick={handleAisShipClick}
                    />

                </MapContainer>
            </div>
        </div>
    )
}