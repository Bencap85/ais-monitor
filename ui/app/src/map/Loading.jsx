import React from 'react';
import './Loading.css';

export default function Loading({ pipelineStatus }) {
  return (
    <div className="loading-dots-overlay">
        <div className="loading-text-div">
            {/* <div className="loading-text">Running Detection</div> */}
            <div className="pipeline-status">{pipelineStatus?.stage} {`${(parseFloat(pipelineStatus?.progress) * 100).toFixed(0)}%`}</div>
            {/* <div className="loading-dots">
            <span>.</span>
            <span>.</span>
            <span>.</span>
            </div> */}
        </div>
    </div>
  );
}
