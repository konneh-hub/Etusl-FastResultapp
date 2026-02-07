import { createSlice } from '@reduxjs/toolkit'

const resultSlice = createSlice({
  name: 'results',
  initialState: {
    data: [],
    loading: false,
    error: null
  },
  reducers: {
    setResults: (state, action) => {
      state.data = action.payload
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
    setError: (state, action) => {
      state.error = action.payload
    }
  }
})

export const { setResults, setLoading, setError } = resultSlice.actions
export default resultSlice.reducer
