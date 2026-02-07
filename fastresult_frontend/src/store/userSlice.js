import { createSlice } from '@reduxjs/toolkit'

const userSlice = createSlice({
  name: 'user',
  initialState: {
    data: null,
    role: null,
    loading: false
  },
  reducers: {
    setUser: (state, action) => {
      state.data = action.payload
      state.role = action.payload.role
    },
    clearUser: (state) => {
      state.data = null
      state.role = null
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    }
  }
})

export const { setUser, clearUser, setLoading } = userSlice.actions
export default userSlice.reducer
