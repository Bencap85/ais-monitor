import Tab from './Tab.jsx';
import { useDispatch, useSelector } from 'react-redux';
import './SidebarHeader.css';
import { DATA_SOURCES } from "../constants/constants.js";


export default function SidebarHeader() {

    const currentMode = useSelector(state => state.currentMode);

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
        <div className="sidebar-header">
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