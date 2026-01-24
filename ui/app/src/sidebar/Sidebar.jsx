import "./Sidebar.css";
import SidebarHeader from './SidebarHeader.jsx';
import SearchBar from './SearchBar.jsx';
import AisShipsList from './AisShipsList.jsx';
import { useState, useEffect, useRef, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { selectAllShips } from '../slice/aisShipsSlice.js';
import { shipTypeToColor } from '../constants/constants.js';
import { DATA_SOURCES } from "../constants/constants.js";


export default function Sidebar({ handleCreateNewZone, 
                                  zones, 
                                  setFlyToLocation,
                                  isLoading }) {
                                    
  const currentMode = useSelector(state => state.currentMode);
  const isMobile = window.innerWidth <= 750;
  const [ isMinimized, setIsMinimized ] = useState(false);
  
  return (
    <div className="sidebar">
      <SidebarHeader isMinimized={isMinimized} setIsMinimized={setIsMinimized} />
      { isMinimized && isMobile ? null : 
        <>
          <SearchBar />
          <AisShipsList isLoading={isLoading} />
        </>
      }
    </div>
  );
}
