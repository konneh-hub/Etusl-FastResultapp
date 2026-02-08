/**
 * API Error Handler
 * Centralized error handling for API requests
 */

export class APIError extends Error {
  constructor(message, statusCode, details) {
    super(message)
    this.statusCode = statusCode
    this.details = details
  }
}

export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response
    const message = data?.message || data?.detail || 'An error occurred'
    
    switch (status) {
      case 400:
        return {
          message: 'Invalid request. Please check your input.',
          details: data?.errors || message,
          statusCode: 400
        }
      case 401:
        return {
          message: 'Authentication failed. Please login again.',
          details: message,
          statusCode: 401
        }
      case 403:
        return {
          message: 'You do not have permission to perform this action.',
          details: message,
          statusCode: 403
        }
      case 404:
        return {
          message: 'Resource not found.',
          details: message,
          statusCode: 404
        }
      case 409:
        return {
          message: 'Conflict: This resource already exists or has been modified.',
          details: message,
          statusCode: 409
        }
      case 429:
        return {
          message: 'Too many requests. Please try again later.',
          details: message,
          statusCode: 429
        }
      case 500:
        return {
          message: 'Server error. Please try again later.',
          details: message,
          statusCode: 500
        }
      case 503:
        return {
          message: 'Service unavailable. The server is temporarily down.',
          details: message,
          statusCode: 503
        }
      default:
        return {
          message: message || 'An unexpected error occurred.',
          statusCode: status
        }
    }
  } else if (error.request) {
    // Request made but no response
    return {
      message: 'No response from server. Please check your connection.',
      statusCode: 0
    }
  } else if (error.code === 'ECONNABORTED') {
    return {
      message: 'Request timeout. Please try again.',
      statusCode: -1
    }
  } else {
    return {
      message: error.message || 'An unexpected error occurred.',
      statusCode: -1
    }
  }
}

export const isClientError = (statusCode) => statusCode >= 400 && statusCode < 500
export const isServerError = (statusCode) => statusCode >= 500
export const isAuthError = (statusCode) => statusCode === 401
export const isForbidden = (statusCode) => statusCode === 403
