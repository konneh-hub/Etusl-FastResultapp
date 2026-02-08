/**
 * Logger utility for debugging and monitoring
 */

const LOG_LEVELS = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR'
}

const isDevelopment = process.env.NODE_ENV === 'development'

const formatLog = (level, message, data) => {
  const timestamp = new Date().toISOString()
  return {
    timestamp,
    level,
    message,
    data
  }
}

const log = (level, message, data = null) => {
  if (!isDevelopment && level === LOG_LEVELS.DEBUG) return

  const formattedLog = formatLog(level, message, data)
  
  switch (level) {
    case LOG_LEVELS.DEBUG:
      console.debug(`[${formattedLog.timestamp}] ${level}:`, message, data)
      break
    case LOG_LEVELS.INFO:
      console.info(`[${formattedLog.timestamp}] ${level}:`, message, data)
      break
    case LOG_LEVELS.WARN:
      console.warn(`[${formattedLog.timestamp}] ${level}:`, message, data)
      break
    case LOG_LEVELS.ERROR:
      console.error(`[${formattedLog.timestamp}] ${level}:`, message, data)
      break
  }

  // Send to analytics/monitoring service in production
  if (!isDevelopment) {
    sendToMonitoring(formattedLog)
  }
}

const sendToMonitoring = (log) => {
  // TODO: Send logs to monitoring service (e.g., Sentry, LogRocket)
  // Example: Sentry.captureMessage(log.message, log.level)
}

export default {
  debug: (message, data) => log(LOG_LEVELS.DEBUG, message, data),
  info: (message, data) => log(LOG_LEVELS.INFO, message, data),
  warn: (message, data) => log(LOG_LEVELS.WARN, message, data),
  error: (message, data) => log(LOG_LEVELS.ERROR, message, data),
  group: (groupName) => console.group(groupName),
  groupEnd: () => console.groupEnd(),
  time: (label) => console.time(label),
  timeEnd: (label) => console.timeEnd(label)
}
