import { createSlice, createEntityAdapter, createSelector } from '@reduxjs/toolkit';
import { selectQuery } from './searchSlice'; // import the query selector
import { NAVIGATIONAL_STATUSES } from '../constants/constants';

const aisShipsAdapter = createEntityAdapter({
  selectId: (ship) => ship.mmsi, // Use MMSI as the unique ID
});

const aisShipsSlice = createSlice({
  name: 'aisShips',
  initialState: aisShipsAdapter.getInitialState(),
  reducers: {
    upsertShips: aisShipsAdapter.upsertMany,
    removeShip: aisShipsAdapter.removeOne,
    clearShips: aisShipsAdapter.removeAll,
    setShips: aisShipsAdapter.setAll
  },
});

export const { upsertShips, removeShip, clearShips, setShips } = aisShipsSlice.actions;
export default aisShipsSlice.reducer;

// Base selectors from the adapter
export const {
  selectById: selectShipByMmsi,
  selectAll: selectAllShips,
  selectIds: selectShipIds,
} = aisShipsAdapter.getSelectors((state) => state.aisShips);

// Derived selector: ships filtered by query
export const selectFilteredShips = createSelector(
  [selectAllShips, selectQuery],
  (allShips, query) => {
    if (!query) return allShips;
    const q = query.toLowerCase().trim();
    return allShips.filter(ship =>
      ship.mmsi?.toString().toLowerCase().includes(q) ||
      NAVIGATIONAL_STATUSES[ship.NavigationalStatus]?.toLowerCase().includes(query.toLowerCase()) ||
      ship.Name?.toString().toLowerCase().trim().includes(q) ||
      ship.ShipTypeName?.toString().toLowerCase().trim().includes(q)
      
    );
  }
);
