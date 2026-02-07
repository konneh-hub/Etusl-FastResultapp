import { configureStore } from '@reduxjs/toolkit'
import authReducer from './authSlice'
import userReducer from './userSlice'
import resultReducer from './resultSlice'
import academicReducer from './academicSlice'
import notificationReducer from './notificationSlice'

const store = configureStore({
  reducer: {
    auth: authReducer,
    user: userReducer,
    results: resultReducer,
    academic: academicReducer,
    notifications: notificationReducer
  }
})

export default store
