import { createSlice } from '@reduxjs/toolkit';


const selectedShipSlice = createSlice({
  name: 'selectedShip',
  initialState: null,
  reducers: {
    setSelectedShip: (state, action) => action.payload
    }
});


export const { setSelectedShip } = selectedShipSlice.actions;
export default selectedShipSlice.reducer;