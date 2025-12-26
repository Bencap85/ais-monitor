import { MapContainer, TileLayer, useMap, Marker, Popup, Polygon, GeoJSON, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setSelectedShip } from '../../slice/selectedShipSlice.js';
import { selectAllShips, selectShipByMmsi, upsertShips, selectFilteredShips, clearShips, setShips } from '../../slice/aisShipsSlice.js';
import { store } from '../../store.js';
import { SHIP_STATUSES, NAVIGATIONAL_STATUS, CODE_TO_NAVIGATIONAL_STATUS } from '../../constants/constants.js';
import { getMarkerColor, getMarkerShape, MARKER_SHAPE } from '../../AisShipMarkerConfig.js';
import ReactDOM from 'react-dom';
import React from 'react';
import TileTracker from '../TileTracker.jsx';
import CenterLogger from '../CenterLogger.jsx';
import './AisMap.css';
import 'leaflet/dist/leaflet.css';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
const { io } = require("socket.io-client");


const WS_URL = process.env.REACT_APP_WS_URL;

export default function ShipSocketListener({ visibleTilesRef, handleAisShipClick, mapContext }) {
    /*
    * This component listens for positions via websocket and updates redux store.
    */
    const map = useMap();

    const ships = useSelector(selectFilteredShips);
    const lastTilesRef = useRef([]);
    const socketRef = useRef(null);
    const selectedShip = useSelector(state => state.selectedShip);

    const metrics = useRef({});

    const updateBuffer = useRef([]);
    const BUFFER_DELAY_MS = 1000;
    
    const dispatch = useDispatch();

    const tileObjToRoom = (tileObj) => {
        return `${tileObj.z}_${tileObj.x}_${tileObj.y}`
    }

    const normalizeShip = (ship) => {
        return {
            ...ship,
            mmsi: Number(ship.UserID)
        }
    }

    const resetMetrics = () => {
        return {
            startTime: new Date(),
            messages: 0
        }
    }

    useEffect(() => {
        const socket = io(WS_URL);
        socketRef.current = socket;

        socket.on("connect", () => {

            metrics.current = resetMetrics();
            console.log("Metrics.startTime = " + metrics.current.startTime);
            console.log("Metrics.messages = " + metrics.current.messages);

            socket.emit("subscribe_tiles", { tiles: [] });

            socket.on("ais_update", (data) => {

                // Determine if this ship is within the viewport
                const viewportBounds = mapContext.current?.viewportBoundsGeojson?.geometry?.coordinates
                const cornersList = viewportBounds[0];

                let minLng = 100000;
                let maxLng = -100000;
                for (let i = 0; i < cornersList.length; i++) {
                    const currentLng = cornersList[i][0];
                    if (currentLng < minLng) minLng = currentLng;
                    if (currentLng > maxLng) maxLng = currentLng;
                }

                let minLat = 100000;
                let maxLat = -100000;
                for (let i = 0; i < cornersList.length; i++) {
                    const currentLat = cornersList[i][1];
                    if (currentLat < minLat) minLat = currentLat;
                    if (currentLat > maxLat) maxLat = currentLat;
                }
                
                if (data.Longitude < minLng || data.Longitude > maxLng
                    || data.Latitude < minLat || data.Latitude > maxLat) {
                        return;
                }

                // Update messagesPerSecond
                metrics.current.messages += 1;
                const msgPerSec = metrics.current?.messages / ((new Date() - metrics.current?.startTime) / 1000);
                
                // console.log("Metrics.startTime: " + metrics.current.startTime);
                // console.log("Metrics.messages: " + metrics.current.messages);
                // console.log(`Recieving ${msgPerSec} messages per second`);

                // Reset metrics to get an accurate average
                if (metrics.current.messages >= 25) {
                    metrics.current = resetMetrics();
                }  

                const normalizedShip = normalizeShip({...data, Timestamp: new Date().toISOString() });
                
                // Update selected ship
                if (data.UserID === selectedShip?.mmsi) {
                    normalizedShip = { ...selectedShip, ...normalizedShip };
                }

                // Add ship to buffer to update redux
                updateBuffer.current.push(normalizedShip);

            });
        });

        return () => socket.disconnect();
    }, [map]);


    useEffect(() => {
        let delay = 5000; // default
        let intervalId;

        const startInterval = () => {
            intervalId = setInterval(() => {
                dispatch(upsertShips(updateBuffer.current));
                updateBuffer.current = [];

                // Recalculate messages per second
                let msgPerSec;
                if(metrics.current.messages === 0) {
                    // Some default value
                    msgPerSec = 50;
                } else {
                    const diffSeconds = (Date.now() - metrics.current.startTime) / 1000;
                    msgPerSec = metrics.current.messages / diffSeconds;
                }

                // Adjust delay thresholds
                let newDelay;
                if (msgPerSec < 2) newDelay = 500
                else if (msgPerSec < 5) newDelay = 1000;
                else if (msgPerSec < 20) newDelay = 3000;
                else newDelay = 5000;

                // If delay changed, restart interval
                if (newDelay !== delay) {
                    clearInterval(intervalId);
                    delay = newDelay;
                    startInterval();
                }
            }, delay);
        };

        startInterval();

        return () => clearInterval(intervalId);
    }, []);
    

    useEffect(() => {
        const observer = setInterval(() => {
            let currentTiles = visibleTilesRef.current;
            const lastTiles = lastTilesRef.current;

            // Set tile subscription to empty if we are subscribed to too many tiles.
            if (currentTiles?.length >= 4) {
                currentTiles = [];
            }
    
            const changed = JSON.stringify(currentTiles) !== JSON.stringify(lastTiles);
            if (changed && socketRef.current) {
                const rooms = currentTiles.map(tile => tileObjToRoom(tile));
                socketRef.current.emit("subscribe_tiles", { tiles: rooms });
                console.log("Updated tile subscription:", rooms);
                lastTilesRef.current = currentTiles;
            }
        }, 500); // check every 500ms

        return () => clearInterval(observer);
    }, []);

    

    return null;
}