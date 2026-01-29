import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { useEffect, useRef } from 'react';
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


const REPOSITORY_SERVICE_BASE_URL = process.env.REACT_APP_REPOSITORY_SERVICE_BASE_URL;
const TRAIL_COLOR = "red";
const SELECTED_TRAIL_COLOR = "red";
const SELECTED_SHIP_COLOR = "white";


export default function ShipMarkerDrawer({ handleAisShipClick }) {
    /*
    * This component reads positions from redux and draws markers.
    */
    const map = useMap();

    // Maintains a map<mmsi, marker> of the markers on the map
    const shipMarkersRef = useRef(new Map());

    // Maintains a map<mmsi, segments> of the trails per ship
    const shipsTrailRef = useRef({});   
    const historyMarkersRef = useRef([]);

    const ships = useSelector(selectFilteredShips);
    const selectedShip = useSelector(state => state.selectedShip);

    // lastSelectedShip tracked in ref. Allows rendering logic to determine if it is drawing or updating.
    const lastSelectedShipRef = useRef({});

    const dispatch = useDispatch();

    const clusterGroupRef = useRef(L.markerClusterGroup({
        disableClusteringAtZoom: 10,
        maxClusterRadius: 60,
        iconCreateFunction: cluster => {
            const markers = cluster.getAllChildMarkers();
            const count = markers.length;

            // Doesn't seem to be working
            const containsSelected = markers.some(m => m.options.mmsi === selectedShip?.mmsi);

            return L.divIcon({
                html: `<span>${count}</span>`,
                className: containsSelected ? 'highlight-cluster' : 'custom-cluster',
                iconSize: L.point(40, 40)
            });
        }
    }));

    useEffect(() => {
        map.addLayer(clusterGroupRef.current);
    }, [map]);

    // Update selectedShip marker on redux data change
    useEffect(() => {

        // Reset last selected color (if different)
        if (lastSelectedShipRef?.current && lastSelectedShipRef?.current.mmsi !== selectedShip?.mmsi) {
            
            const shipColor = getMarkerColor(lastSelectedShipRef.current);
            const markerShape = getMarkerShape(lastSelectedShipRef.current);

            shipMarkersRef.current.get(lastSelectedShipRef.current.mmsi)
            ?.setIcon(createAisShipIcon(lastSelectedShipRef.current.TrueHeading, shipColor, markerShape));
        
        }

        if (!selectedShip) {
            lastSelectedShipRef.current = null;
            clearHistoryMarkers();
            clearTrails();
            return;
        }

        highlightShip(selectedShip);
        if (clusterGroupRef.current) {
            // This forces markercluster to rebuild all cluster icons
            clusterGroupRef.current.refreshClusters();
        }

        // If this is an update to the same selected ship, draw new trail segment
        console.log({ lastMmsi: lastSelectedShipRef?.current?.mmsi, currentMmsi: selectedShip?.mmsi});
        if (lastSelectedShipRef?.current?.mmsi === selectedShip?.mmsi) {
            const prevLatLng = [ lastSelectedShipRef.current.Latitude, lastSelectedShipRef.current.Longitude ];
            const latLng = [ selectedShip.Latitude, selectedShip.Longitude ];
            const prevPointData = {
                Sog: lastSelectedShipRef.current.Sog,
                Timestamp: lastSelectedShipRef.current.Timestamp,
                TrueHeading: lastSelectedShipRef.current.TrueHeading
            };
            const pointData = {
                Sog: selectedShip.Sog,
                Timestamp: selectedShip.Timestamp,
                TrueHeading: selectedShip.TrueHeading
            };

            updateAisShipMarker(shipMarkersRef.current.get(selectedShip.mmsi), selectedShip);
            drawTrail(prevLatLng, latLng, selectedShip.mmsi, prevPointData, pointData);

        } else {
            
            clearTrails();
            clearHistoryMarkers();

            const mmsi = selectedShip.mmsi;

            const twentyFourHoursAgoUtc = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
            const startTime = twentyFourHoursAgoUtc;
            const endTime = new Date().toISOString();

            fetch(`${REPOSITORY_SERVICE_BASE_URL}/ships/${mmsi}/history?startTime=${startTime}&endTime=${endTime}`)
                .then(response => response.json())
                .then(data => {

                    // Sort ascending by timestamp
                    data = data?.sort((a, b) => new Date(a.Timestamp) - new Date(b.Timestamp));

                    for (let i = 0; i < data?.length-1; i++) {
                        
                        const prevLatLng = [ data[i].Latitude, data[i].Longitude ];
                        const currentLatLng = [ data[i+1].Latitude, data[i+1].Longitude ];

                        const popupDataPrev = {
                            ...data[i],
                            Timestamp: data[i].Timestamp
                        }

                        const popupDataCurrent = {
                            ...data[i+1],
                            Timestamp: data[i+1].Timestamp
                        }

                        drawTrail(prevLatLng, currentLatLng, mmsi, popupDataPrev, popupDataCurrent);

                    }
                })
        }
        
        lastSelectedShipRef.current = selectedShip;

    }, [selectedShip]);

    // Draw ships on redux data change
    useEffect(() => {

        function drawShips() {
            const startTime = performance.now();

            const currentMmsis = new Set(ships.map(s => s.mmsi));
            const existingMmsis = new Set(shipMarkersRef.current.keys().map(Number));

            // Add ship markers that do not exist. Do not render yet.
            ships.forEach(ship => {
                if (!existingMmsis.has(ship.mmsi)) {
                    const marker = createAisShipMarker(ship);
                    shipMarkersRef.current.set(ship.mmsi, marker);
                } 
            });

            // Do not render ships outside current search (Helps with performance, seems to pan/zoom more smoothly)
            for (const mmsi of existingMmsis) {
                if (!currentMmsis.has(mmsi)) {
                    shipMarkersRef.current.delete(mmsi);
                }
            }

            // Remove malformed ship markers
            for (const key of shipMarkersRef.current.keys()) {
                if (!shipMarkersRef.current.get(key) ||
                !shipMarkersRef.current.get(key).getLatLng()) {
                    console.log("Removed malformed ship");
                    shipMarkersRef.current.delete(key);
                }
            }

            // Render ship markers all at once
            clusterGroupRef.current.clearLayers();
            clusterGroupRef.current.addLayers(Array.from(shipMarkersRef.current.values()));

            // For ship markers existing before this render, update their positions
            ships.forEach(ship => {
                if (existingMmsis.has(ship.mmsi)) {
                    updateAisShipMarker(shipMarkersRef.current.get(ship.mmsi), ship);
                }
            });
            

            const endTime = performance.now();
            const elapsed = (endTime - startTime) / 1000;
            console.log(`Rendering took ${elapsed.toFixed(2)} seconds`);
        }
        drawShips(ships, shipMarkersRef, selectedShip, clusterGroupRef);
    
    }, [ships]);

    const highlightShip = (ship) => {

        const marker = shipMarkersRef.current.get(ship.mmsi);
        if (!marker) return;

        const markerShape = getMarkerShape(ship);
        const highlightIcon = createAisShipIcon(ship.TrueHeading, SELECTED_SHIP_COLOR, markerShape);
        marker.setIcon(highlightIcon);

    }

    const createAisShipIcon = (heading, color, shape) => {
        let shapeHtml;

        switch (shape) {
            case MARKER_SHAPE.CIRCLE:
                shapeHtml = `<circle class="ais-ship-icon-polygon" cx="10" cy="20" r="6" fill="${color}" />`;
                break;
            case MARKER_SHAPE.SQUARE:
                shapeHtml = `<rect class="ais-ship-icon-polygon" x="4" y="12" width="12" height="12" fill="${color}" />`;
                break;
            case MARKER_SHAPE.SHIP:
            default:
                shapeHtml = `<polygon class="ais-ship-icon-polygon" points="10,0 18,8 18,50 2,50 2,8" fill="${color}" />`;
                break;
        }

        const svgIcon = L.divIcon({
            className: "ais-ship-icon",
            html: `
            <div class="pulse-wrapper">
                <svg class="ais-ship-icon" width="10" height="20" viewBox="0 0 20 40"
                    style="transform: rotate(${heading !== 511 ? heading : 0}deg);">
                ${shapeHtml}
                </svg>
            </div>
            `,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });

        return svgIcon;
    };

    const createAisShipMarker = (ship) => {
        if (!ship || !ship.Latitude || !ship.Longitude) {
            return;
        }

        const shipColor = getMarkerColor(ship);
        const heading = ship.TrueHeading || 0;
        const markerShape = getMarkerShape(ship);
        const svgIcon = createAisShipIcon(heading, shipColor, markerShape);
        const latlng = [ship?.Latitude, ship?.Longitude];
        
        const marker = L.marker(latlng, { 
            icon: svgIcon,
            heading: heading,
            mmsi: ship.mmsi
        });

        marker.on('click', () => {
            handleClick(ship.mmsi);
        });

        const popupContent = `
                <div class=${"history-popup"}>
                    <span class="key">Name:</span> ${ship.Name || "Unknown"}<br/>
                    <span class="key">Type:</span> ${ship.ShipTypeName?.split(",")[0] || "Unknown"}<br/>
                </div>
            `;

        marker.bindTooltip(popupContent, {
                direction: "top",
                className: "history-popup"
            });

        return marker;
    }

    function handleClick(mmsi) {
        const state = store.getState();
        const latestShip = selectShipByMmsi(state, mmsi);
        if (latestShip) {
            handleAisShipClick(latestShip);
        }
    }

    const updateAisShipMarker = (marker, newShipData) => {
        
        if (!newShipData || !newShipData.Latitude || !newShipData.Longitude) {
            return;
        }

        // Rotate icon to correct heading
        const heading = newShipData.TrueHeading || 0;
        const el = marker.getElement();
        if (el) {
            const icon = el.querySelector('.ais-ship-icon');

            const rotation = heading !== 511 ? heading : 0;
            const iconColor = getMarkerColor(newShipData);

            icon.style.transform = `rotate(${rotation}deg)`;
            icon.style.fill = iconColor;
        }

        const start = marker.getLatLng();
        const end = L.latLng(newShipData.Latitude, newShipData.Longitude);
        const duration = 0;

        if (start.equals(end)) {
            return;
        }

        marker.setLatLng(end);
        flashShipMarker(marker);
        return marker;
        
    }

    const flashShipMarker = (marker) => {
        // Get the DOM element and apply the flash class
        const el = marker.getElement();
        if (el) {
            const polygon = el.querySelector('.ais-ship-icon-polygon');
            if (polygon) {
                // Store original fill color in a CSS variable
                const originalFill = polygon.getAttribute('fill');
                polygon.style.setProperty('--ship-color', originalFill);

                polygon.classList.add('flash-white');
                polygon.addEventListener('animationend', () => {
                    polygon.classList.remove('flash-white');
                }, { once: true });
            }
        }
    }

    const clearTrails = () => {
        Object.values(shipsTrailRef.current).forEach(trailSegments => {
            trailSegments.forEach(segment => {
                map.removeLayer(segment);   // remove from map
            });
        });
        shipsTrailRef.current = {};     // reset ref
    }

    const clearHistoryMarkers = () => {
        historyMarkersRef.current.forEach(marker => {
            map.removeLayer(marker);
        });
        historyMarkersRef.current = [];
    }

    const highlightTrail = (mmsi) => {

        clearTrails();
        clearHistoryMarkers();

        // Highlight selected ship's trail
        const selectedTrail = shipsTrailRef.current[mmsi];
        if (selectedTrail) {
            selectedTrail.forEach(segment => {
                segment.setStyle({
                    color: SELECTED_TRAIL_COLOR,
                    weight: 2,
                    opacity: 1
                });
            });
        }
    }

    function drawTrail(prevLatLng, latLng, mmsi, prevPointData, pointData) {

        const trailSegment = L.polyline([prevLatLng, latLng], {
            color: TRAIL_COLOR,
            weight: 0.5,
            opacity: 1
        }).addTo(map);

        const trailPopupClassName = "history-popup";

        if (prevPointData && pointData) {
            // Add popups with relevant info
            const popupContentPrev = `
                <div class=${trailPopupClassName}>
                    <span class="key">Speed:</span> ${prevPointData.Sog} knots<br/>
                    <span class="key">Heading:</span> ${prevPointData.TrueHeading}°<br/>
                    <span class="key">Time:</span> ${new Date(prevPointData.Timestamp).toISOString().split("T")[1].split(".")[0]} GMT
                </div>
            `;
            const popupContent = `
                <div class=${trailPopupClassName}>
                    <span class="key">Speed:</span> ${pointData.Sog} knots<br/>
                    <span class="key">Heading:</span> ${pointData.TrueHeading}°<br/>
                    <span class="key">Time:</span> ${new Date(pointData.Timestamp).toISOString().split("T")[1].split(".")[0]} GMT
                </div>
            `;

            const prevMarker = L.circleMarker(prevLatLng, {
                    radius: 0.1,
                    color: TRAIL_COLOR,
                    opacity: 0
                }).addTo(map);

            prevMarker.bindTooltip(popupContentPrev, {
                    direction: "top",
                    className: trailPopupClassName
                });

            const marker = L.circleMarker(latLng, {
                radius: 0.1,
                color: TRAIL_COLOR,
                opacity: 0
            }).addTo(map);

            marker.bindTooltip(popupContent, {
                direction: "top",
                className: trailPopupClassName
            });

            historyMarkersRef.current.push(prevMarker);
            historyMarkersRef.current.push(marker);
        }

        if (!shipsTrailRef.current[mmsi]) {
            shipsTrailRef.current[mmsi] = [];
        }
        shipsTrailRef.current[mmsi] = [ ...shipsTrailRef.current[mmsi], trailSegment];
    }
        

    return null;
}