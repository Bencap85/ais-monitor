import Tab from './Tab.jsx';
import { useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './SidebarHeader.css';
import { DATA_SOURCES } from "../constants/constants.js";


export default function SidebarHeader({ isMinimized, setIsMinimized }) {

    const currentMode = useSelector(state => state.currentMode);

    // Add double tap open/close for mobile
    const lastTapRef = useRef(0);
    const handleTap = () => {
        const DOUBLE_TAP_THRESHOLD_MS = 200;
        const NOW = Date.now();

        if (NOW - lastTapRef.current < DOUBLE_TAP_THRESHOLD_MS) {
            setIsMinimized(!isMinimized);
        }
        lastTapRef.current = NOW;
    }

    const satelliteTab = {
        name: "Satellite (Legacy)",
        dataSource: DATA_SOURCES.SATELLITE
    }

    const aisTab = {
        name: "AIS Feed",
        dataSource: DATA_SOURCES.AIS
    }

    const tabs = [ aisTab, satelliteTab ];

    for (const tab of tabs) {
        console.log(JSON.stringify(tab));
    }

    return(
        <div className="sidebar-header" onClick={handleTap}>
            <div className="tabs">
                {tabs.map(tab => {
                    return(
                        <Tab name={tab.name}
                             dataSource={tab.dataSource}
                             selected={tab.dataSource === currentMode} />
                    )
                })}
            </div>
        </div>
    )

}