import { createSlice } from '@reduxjs/toolkit';
import { DATA_SOURCES } from '../constants/constants.js';


const currentModeSlice = createSlice({
  name: 'currentMode',
  initialState: DATA_SOURCES.SATELLITE,
  reducers: {
    setCurrentMode: (state, action) => action.payload
  }
});


export const { setCurrentMode } = currentModeSlice.actions;
export default currentModeSlice.reducer;