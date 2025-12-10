import { createSlice } from '@reduxjs/toolkit';

const searchSlice = createSlice({
  name: 'search',
  initialState: { query: '' },
  reducers: {
    setQuery: (state, action) => {
      state.query = action.payload;
    },
    clearQuery: (state) => {
      state.query = '';
    }
  }
});

export const { setQuery, clearQuery } = searchSlice.actions;
export default searchSlice.reducer;

// Selector
export const selectQuery = (state) => state.search.query;