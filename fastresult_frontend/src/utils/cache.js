/**
 * Caching utilities for API responses
 */

const cache = new Map()
const cacheExpirations = new Map()

const DEFAULT_TTL = 5 * 60 * 1000 // 5 minutes

export const setCache = (key, value, ttl = DEFAULT_TTL) => {
  cache.set(key, value)
  
  if (ttl > 0) {
    const expirationTime = Date.now() + ttl
    cacheExpirations.set(key, expirationTime)
  }
}

export const getCache = (key) => {
  const expirationTime = cacheExpirations.get(key)
  
  if (expirationTime && Date.now() > expirationTime) {
    cache.delete(key)
    cacheExpirations.delete(key)
    return null
  }
  
  return cache.get(key) || null
}

export const hasCache = (key) => {
  const cachedValue = getCache(key)
  return cachedValue !== null
}

export const deleteCache = (key) => {
  cache.delete(key)
  cacheExpirations.delete(key)
}

export const clearCache = () => {
  cache.clear()
  cacheExpirations.clear()
}

export const invalidatePattern = (pattern) => {
  const regex = new RegExp(pattern)
  const keysToDelete = Array.from(cache.keys()).filter(key => regex.test(key))
  
  keysToDelete.forEach(key => {
    cache.delete(key)
    cacheExpirations.delete(key)
  })
}

export const getCacheSize = () => {
  return cache.size
}

export const getCacheInfo = () => {
  return {
    size: cache.size,
    keys: Array.from(cache.keys()),
    expirations: Array.from(cacheExpirations.entries()).reduce((acc, [key, time]) => ({
      ...acc,
      [key]: new Date(time).toISOString()
    }), {})
  }
}
