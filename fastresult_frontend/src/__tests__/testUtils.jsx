"""
Frontend test utilities
"""
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import store from '../store/store'

export function renderWithProviders(component) {
  return render(
    <Provider store={store}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </Provider>
  )
}

export function createMockAuthState(overrides = {}) {
  return {
    auth: {
      token: 'test-token',
      isAuthenticated: true,
      loading: false,
      error: null,
      ...overrides
    }
  }
}
