import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from 'react-redux';
import { selectQuery, setQuery } from '../slice/searchSlice.js';
import { FaSearch } from "react-icons/fa";
import "./SearchBar.css";


export default function SearchBar() {

    const query = useSelector(selectQuery);

    const dispatch = useDispatch();
    const [ inputValue, setInputValue ] = useState(query);

    useEffect(() => {
        const handler = setTimeout(() => {
            dispatch(setQuery(inputValue));
        }, 300);

        return () => clearTimeout(handler);
    }, [ inputValue, dispatch ]);

    return (
    <div className="search-bar">
        <div className="search-icon-div">
            <FaSearch className="search-icon" />
        </div>
        <input
            className="search-bar-input"
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={"Search by MMSI, name, type..."}
        />
        <div className="cancel-search-div">
            <button className="cancel-search-button" onClick={() => setInputValue("")}>
                Clear
            </button>
        </div>
    </div>
    );
}