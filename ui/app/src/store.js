import { configureStore } from '@reduxjs/toolkit';
import selectedShipReducer from './slice/selectedShipSlice';
import currentModeReducer from './slice/currentModeSlice';
import aisShipsReducer from './slice/aisShipsSlice';
import searchReducer from './slice/searchSlice.js';

export const store = configureStore({
  reducer: {
    selectedShip: selectedShipReducer,
    currentMode: currentModeReducer,
    aisShips: aisShipsReducer,
    search: searchReducer
  }
});