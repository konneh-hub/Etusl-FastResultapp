/**
 * Storage utilities for localStorage and sessionStorage
 */

const STORAGE_KEY_PREFIX = 'fastresult_'

export const storage = {
  // LocalStorage
  setLocal: (key, value, expiresIn = null) => {
    const prefixedKey = STORAGE_KEY_PREFIX + key
    const data = {
      value,
      timestamp: Date.now(),
      expiresIn
    }
    
    try {
      localStorage.setItem(prefixedKey, JSON.stringify(data))
      return true
    } catch (error) {
      console.error('Failed to save to localStorage:', error)
      return false
    }
  },

  getLocal: (key) => {
    const prefixedKey = STORAGE_KEY_PREFIX + key
    
    try {
      const item = localStorage.getItem(prefixedKey)
      if (!item) return null
      
      const data = JSON.parse(item)
      
      if (data.expiresIn) {
        const elapsed = Date.now() - data.timestamp
        if (elapsed > data.expiresIn) {
          localStorage.removeItem(prefixedKey)
          return null
        }
      }
      
      return data.value
    } catch (error) {
      console.error('Failed to read from localStorage:', error)
      return null
    }
  },

  removeLocal: (key) => {
    const prefixedKey = STORAGE_KEY_PREFIX + key
    localStorage.removeItem(prefixedKey)
  },

  clearLocal: () => {
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (key.startsWith(STORAGE_KEY_PREFIX)) {
        localStorage.removeItem(key)
      }
    })
  },

  // SessionStorage
  setSession: (key, value) => {
    const prefixedKey = STORAGE_KEY_PREFIX + key
    
    try {
      sessionStorage.setItem(prefixedKey, JSON.stringify(value))
      return true
    } catch (error) {
      console.error('Failed to save to sessionStorage:', error)
      return false
    }
  },

  getSession: (key) => {
    const prefixedKey = STORAGE_KEY_PREFIX + key
    
    try {
      const item = sessionStorage.getItem(prefixedKey)
      return item ? JSON.parse(item) : null
    } catch (error) {
      console.error('Failed to read from sessionStorage:', error)
      return null
    }
  },

  removeSession: (key) => {
    const prefixedKey = STORAGE_KEY_PREFIX + key
    sessionStorage.removeItem(prefixedKey)
  },

  clearSession: () => {
    const keys = Object.keys(sessionStorage)
    keys.forEach(key => {
      if (key.startsWith(STORAGE_KEY_PREFIX)) {
        sessionStorage.removeItem(key)
      }
    })
  }
}

export default storage
