import SatelliteShipPopup from './SatelliteShipPopup.jsx';
import AisShipPopup from './AisShipPopup.jsx';
import { DATA_SOURCES } from '../constants/constants.js';
import { useSelector } from 'react-redux';


export default function ShipPopup({ ship }) {

    const currentMode = useSelector(state => state.currentMode);
    
    return(
        <>
        {currentMode === DATA_SOURCES.SATELLITE ? 
            (<SatelliteShipPopup type={ship.type}
                            coordinates={ship.coordinates}
                            confidence={ship.confidence}
                            estimatedLength={ship.estimatedLength}
                            />)
        :
            (<AisShipPopup ship={ship} />)
        }
        </>

    )
}