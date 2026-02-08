import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '../hooks/useAuth'
import store from '../store/store'
import Router from '../router'
import './App.css'

function App() {
  return (
    <Provider store={store}>
      <AuthProvider>
        <BrowserRouter>
          <Router />
          <Toaster position="top-right" />
        </BrowserRouter>
      </AuthProvider>
    </Provider>
  )
}

export default App
