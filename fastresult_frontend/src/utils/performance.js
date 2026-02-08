/**
 * Performance monitoring utilities
 */

const metrics = {}

export const measurePerformance = (label, fn) => {
  const start = performance.now()
  const result = fn()
  const end = performance.now()
  const duration = end - start

  if (!metrics[label]) {
    metrics[label] = []
  }
  
  metrics[label].push({
    duration,
    timestamp: new Date().toISOString()
  })

  if (duration > 1000) {
    console.warn(`[PERF] ${label} took ${duration.toFixed(2)}ms`)
  } else {
    console.debug(`[PERF] ${label} took ${duration.toFixed(2)}ms`)
  }

  return result
}

export const measureAsync = async (label, asyncFn) => {
  const start = performance.now()
  try {
    const result = await asyncFn()
    const end = performance.now()
    const duration = end - start

    if (!metrics[label]) {
      metrics[label] = []
    }
    
    metrics[label].push({
      duration,
      timestamp: new Date().toISOString(),
      success: true
    })

    if (duration > 2000) {
      console.warn(`[PERF] ${label} took ${duration.toFixed(2)}ms`)
    } else {
      console.debug(`[PERF] ${label} took ${duration.toFixed(2)}ms`)
    }

    return result
  } catch (error) {
    const end = performance.now()
    const duration = end - start

    if (!metrics[label]) {
      metrics[label] = []
    }
    
    metrics[label].push({
      duration,
      timestamp: new Date().toISOString(),
      success: false,
      error: error.message
    })

    throw error
  }
}

export const getMetrics = (label = null) => {
  if (label) {
    return metrics[label] || []
  }
  return metrics
}

export const getAverageTime = (label) => {
  const records = metrics[label] || []
  if (records.length === 0) return 0
  
  const sum = records.reduce((acc, r) => acc + r.duration, 0)
  return sum / records.length
}

export const clearMetrics = (label = null) => {
  if (label) {
    delete metrics[label]
  } else {
    Object.keys(metrics).forEach(key => delete metrics[key])
  }
}
