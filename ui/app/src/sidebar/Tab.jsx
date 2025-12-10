import { useDispatch, useSelector } from 'react-redux';
import { setCurrentMode } from '../slice/currentModeSlice.js';
import { setSelectedShip } from '../slice/selectedShipSlice.js';
import "./Tab.css";

export default function Tab({ name,
                             dataSource,
                             selected }) {

    const dispatch = useDispatch();

    function handleClick() {
        dispatch(setCurrentMode(dataSource));
        dispatch(setSelectedShip(null));
    }

    let className = "tab";
    if (selected) {
        className += " selected";
    }

    return(
        <div className={className} onClick={handleClick}>
            <p>{name}</p>
        </div>
    )

}