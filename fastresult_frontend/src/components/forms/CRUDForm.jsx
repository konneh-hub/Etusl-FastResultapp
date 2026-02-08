import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'

const CRUDForm = ({
  title,
  fields = [],
  onSubmit,
  initialData = null,
  loading = false,
  mode = 'create' // 'create' or 'edit'
}) => {
  const [formData, setFormData] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (initialData && mode === 'edit') {
      setFormData(initialData)
    } else {
      const emptyData = {}
      fields.forEach(field => {
        emptyData[field.name] = field.defaultValue || ''
      })
      setFormData(emptyData)
    }
  }, [initialData, mode, fields])

  const handleChange = (e, field) => {
    const { name, value, type, checked } = e.target
    const fieldValue = type === 'checkbox' ? checked : value
    
    setFormData(prev => ({
      ...prev,
      [name]: fieldValue
    }))
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    fields.forEach(field => {
      if (field.required && !formData[field.name]) {
        newErrors[field.name] = `${field.label} is required`
      }
      
      if (field.type === 'email' && formData[field.name]) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(formData[field.name])) {
          newErrors[field.name] = 'Invalid email format'
        }
      }
      
      if (field.type === 'number' && formData[field.name]) {
        if (isNaN(formData[field.name])) {
          newErrors[field.name] = 'Must be a number'
        }
        if (field.min !== undefined && Number(formData[field.name]) < field.min) {
          newErrors[field.name] = `Must be at least ${field.min}`
        }
        if (field.max !== undefined && Number(formData[field.name]) > field.max) {
          newErrors[field.name] = `Must not exceed ${field.max}`
        }
      }
      
      if (field.validate && formData[field.name]) {
        const error = field.validate(formData[field.name])
        if (error) newErrors[field.name] = error
      }
    })
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      toast.error('Please fix the errors in the form')
      return
    }
    
    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } catch (error) {
      console.error('Form submission error:', error)
      if (error.response?.data) {
        const apiErrors = error.response.data
        const newErrors = {}
        Object.keys(apiErrors).forEach(key => {
          newErrors[key] = Array.isArray(apiErrors[key]) 
            ? apiErrors[key][0] 
            : apiErrors[key]
        })
        setErrors(newErrors)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800">{title}</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {fields.map(field => (
          <div key={field.name} className="flex flex-col">
            <label className="text-sm font-medium text-gray-700 mb-1">
              {field.label}
              {field.required && <span className="text-red-500">*</span>}
            </label>
            
            {field.type === 'select' ? (
              <select
                name={field.name}
                value={formData[field.name] || ''}
                onChange={handleChange}
                className={`px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors[field.name] ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isSubmitting || loading}
              >
                <option value="">Select {field.label}</option>
                {field.options?.map(opt => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            ) : field.type === 'textarea' ? (
              <textarea
                name={field.name}
                value={formData[field.name] || ''}
                onChange={handleChange}
                rows={4}
                className={`px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors[field.name] ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isSubmitting || loading}
                placeholder={field.placeholder}
              />
            ) : field.type === 'checkbox' ? (
              <input
                type="checkbox"
                name={field.name}
                checked={formData[field.name] || false}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                disabled={isSubmitting || loading}
              />
            ) : (
              <input
                type={field.type || 'text'}
                name={field.name}
                value={formData[field.name] || ''}
                onChange={handleChange}
                className={`px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors[field.name] ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isSubmitting || loading}
                placeholder={field.placeholder}
                min={field.min}
                max={field.max}
              />
            )}
            
            {errors[field.name] && (
              <p className="text-red-500 text-sm mt-1">{errors[field.name]}</p>
            )}
          </div>
        ))}
      </div>
      
      <div className="flex gap-2 pt-4">
        <button
          type="submit"
          disabled={isSubmitting || loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {isSubmitting ? 'Saving...' : mode === 'create' ? 'Create' : 'Update'}
        </button>
        <button
          type="button"
          onClick={() => window.history.back()}
          className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}

export default CRUDForm
