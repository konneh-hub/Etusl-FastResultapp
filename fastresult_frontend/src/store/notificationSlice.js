import { createSlice } from '@reduxjs/toolkit'

const notificationSlice = createSlice({
  name: 'notifications',
  initialState: {
    items: [],
    unread_count: 0
  },
  reducers: {
    setNotifications: (state, action) => {
      state.items = action.payload
    },
    addNotification: (state, action) => {
      state.items.unshift(action.payload)
      state.unread_count += 1
    },
    markAsRead: (state, action) => {
      const notification = state.items.find(n => n.id === action.payload)
      if (notification && !notification.read) {
        notification.read = true
        state.unread_count -= 1
      }
    },
    setUnreadCount: (state, action) => {
      state.unread_count = action.payload
    }
  }
})

export const { setNotifications, addNotification, markAsRead, setUnreadCount } = notificationSlice.actions
export default notificationSlice.reducer
