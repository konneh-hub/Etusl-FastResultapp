import { createSlice } from '@reduxjs/toolkit'

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token'),
    loading: false,
    error: null
  },
  reducers: {
    setToken: (state, action) => {
      state.token = action.payload
      state.isAuthenticated = true
      localStorage.setItem('token', action.payload)
    },
    removeToken: (state) => {
      state.token = null
      state.isAuthenticated = false
      localStorage.removeItem('token')
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
    setError: (state, action) => {
      state.error = action.payload
    }
  }
})

export const { setToken, removeToken, setLoading, setError } = authSlice.actions
export default authSlice.reducer
