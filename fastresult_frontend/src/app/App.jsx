import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import store from '../store/store'
import Router from '../router'
import './App.css'

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Router />
        <Toaster position="top-right" />
      </BrowserRouter>
    </Provider>
  )
}

export default App
