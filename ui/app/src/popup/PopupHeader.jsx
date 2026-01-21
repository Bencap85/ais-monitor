import { useState } from 'react';
import "./PopupHeader.css";

export default function PopupHeader({ title,
                                      handleMinimize,
                                      handleExpand,
                                      handleClose
}) {

    const [ closed, setClosed ] = useState(false);

    const handleMinimizeClick = () => {
        handleMinimize();
    }

    const handleCloseClick = () => {
        setClosed(!closed);
        handleClose();
    }

    const handleExpandClick = () => {
        handleExpand();
    }

    return (
        !closed && (
            <div className="popup-header">
                <div className="popup-title">
                    {title}
                </div>
                <div className="popup-controls">
                    <button className="control minimize" onClick={handleMinimizeClick}>
                        -
                    </button>
                    <button className="control expand" onClick={handleExpandClick}>
                        ⛶
                    </button>
                    <button className="control close" onClick={handleCloseClick}>
                        x
                    </button>
                </div>
            </div>
        )
    );
}