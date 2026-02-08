/**
 * API Response Handler
 * Standardized response handling
 */

export const parseResponse = (response) => {
  return {
    status: response.status,
    statusCode: response.status,
    data: response.data,
    headers: response.headers,
    isSuccess: response.status >= 200 && response.status < 300
  }
}

export const getPaginatedData = (response) => {
  const data = response.data || {}
  return {
    items: data.results || data.data || [],
    total: data.count || data.total || 0,
    page: data.page || 1,
    pageSize: data.page_size || 10,
    nextUrl: data.next || null,
    previousUrl: data.previous || null,
    hasNext: !!(data.next || (data.page && data.total > data.page * data.page_size))
  }
}

export const handleResponseMetadata = (response) => {
  const data = response.data || {}
  return {
    timestamp: data.timestamp || new Date().toISOString(),
    message: data.message || null,
    version: data.version || 'v1',
    requestId: response.headers['x-request-id'] || null
  }
}
