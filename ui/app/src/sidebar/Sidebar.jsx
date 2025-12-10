import "./Sidebar.css";
import ZoneWrapper from './zone/ZoneWrapper.jsx';
import SidebarHeader from './SidebarHeader.jsx';
import SearchBar from './SearchBar.jsx';
import AisShipsList from './AisShipsList.jsx';
import { useState, useRef, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { selectAllShips } from '../slice/aisShipsSlice.js';
import { shipTypeToColor } from '../constants/constants.js';
import { DATA_SOURCES } from "../constants/constants.js";


export default function Sidebar({ handleCreateNewZone, 
                                  zones, 
                                  setFlyToLocation,
                                  isLoading }) {

  const currentMode = useSelector(state => state.currentMode);

  
  return (

    <div className="sidebar">
      <SidebarHeader />
      { currentMode === DATA_SOURCES.SATELLITE &&
        <div className="zones-list">
          <div className="zones-list-header">
            <p className="zones-list-header-text">{zones?.length} Zone{zones?.length > 1 ? "s" : null}</p>
          </div>
          {zones.map(zone => {
            return <ZoneWrapper zone={zone} 
                                setFlyToLocation={setFlyToLocation} />
          })}
          
        </div>
      }
      { currentMode === DATA_SOURCES.AIS &&
        <>
          <SearchBar />
          <AisShipsList isLoading={isLoading} />
        </>
      }
    </div>
  );
}
