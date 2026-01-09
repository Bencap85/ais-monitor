
import { useSelector, useDispatch } from 'react-redux';
import { useState } from 'react';
import { NAVIGATIONAL_STATUSES } from '../constants/constants.js';
import { selectAllShips, clearShips, upsertShips, selectFilteredShips  } from '../slice/aisShipsSlice.js';
import { setSelectedShip } from '../slice/selectedShipSlice.js';
import AisShipsListItem from './AisShipsListItem.jsx';
import "./AisShipsList.css";

export default function AisShipsList({ isLoading }) {

    const dispatch = useDispatch();
    const [ expanded, setExpanded ] = useState(true);
    const [ page, setPage ] = useState(0);
    const shipsToDisplay = useSelector(selectFilteredShips);
    
    let pageSize = 100;
    let pageCount = Math.ceil(shipsToDisplay.length / pageSize);

    const paginatedShips = shipsToDisplay.slice(
        page * pageSize,
        (page + 1) * pageSize
    );

    const onClick = (ship) => {
        dispatch(setSelectedShip(ship));
    }

    return (
        <div className="ais-ships-list">
            <div className="total-vessels">

                <div className="ship-count-container">
                    {isLoading ? 
                        "Loading..." : 
                        <>
                            <div className="live-indicator"></div>
                            <span>{shipsToDisplay?.length} vessels found</span>
                        </>
                    }
                </div>
                <div className="ais-ships-list-header">
                    <div className="ais-ships-list-header-title">
                        VESSELS LIST
                    </div>
                    <div className="ais-ships-list-expand-icon-wrapper" onClick={() => setExpanded(!expanded)}>
                        {expanded ? 
                            <img className={"ais-ships-list-expand-icon"} src="/icons/zone-expand.svg" style={{'transform': 'rotate(90deg)', 'transform-origin': 'center' }}/> : 
                            <img className={"ais-ships-list-expand-icon"} src="/icons/zone-expand.svg" /> 
                        }
                    </div>
                </div>
            </div>

            <div className="ships-list-wrapper">
                {expanded && paginatedShips.map(ship => 
                    <AisShipsListItem key={ship.mmsi} ship={ship} onClick={onClick} />
                )}
            </div>
            {(true) && (
                <div className="sidebar-footer">
                    <div className="pagination-controls">
                        <button disabled={page === 0} onClick={() => setPage(page - 1)}>Prev</button>
                        <span>Page {page + 1}</span>
                        <button
                            disabled={(page + 1) * pageSize >= shipsToDisplay.length}
                            onClick={() => setPage(page + 1)}
                        >
                        Next
                        </button>
                    </div>
                    <div className="version-tag">
                        <p>v{process.env.REACT_APP_UI_VERSION}</p>
                    </div>
                </div>
                )}
        </div>
    );
}