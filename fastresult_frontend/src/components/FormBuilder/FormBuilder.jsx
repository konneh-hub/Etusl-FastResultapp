import React, { useState } from 'react'
import './Form.css'

/**
 * FormBuilder: Dynamic form generator from field definitions
 * Props:
 * - fields: array of {name, label, type, required, options?, placeholder?, value?}
 * - onSubmit: callback(formData) on form submit
 * - onCancel: callback() on cancel
 * - loading: boolean to disable submit button during submission
 * - title: optional form title
 */
export default function FormBuilder({
  fields = [],
  onSubmit,
  onCancel,
  loading = false,
  title = null,
  initialData = {}
}) {
  const [formData, setFormData] = useState(initialData)
  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const validateForm = () => {
    const newErrors = {}
    fields.forEach(field => {
      if (field.required && !formData[field.name]) {
        newErrors[field.name] = `${field.label} is required`
      }
    })
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validateForm()) {
      onSubmit(formData)
    }
  }

  return (
    <form className="form-builder" onSubmit={handleSubmit}>
      {title && <h3>{title}</h3>}

      {fields.map(field => (
        <div key={field.name} className="form-group">
          <label htmlFor={field.name}>
            {field.label}
            {field.required && <span className="required">*</span>}
          </label>

          {field.type === 'select' ? (
            <select
              id={field.name}
              name={field.name}
              value={formData[field.name] || ''}
              onChange={handleChange}
              disabled={loading}
              required={field.required}
            >
              <option value="">{field.placeholder || 'Select...'}</option>
              {field.options?.map(opt => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          ) : field.type === 'textarea' ? (
            <textarea
              id={field.name}
              name={field.name}
              value={formData[field.name] || ''}
              onChange={handleChange}
              placeholder={field.placeholder}
              disabled={loading}
              required={field.required}
              rows={4}
            />
          ) : field.type === 'checkbox' ? (
            <input
              id={field.name}
              type="checkbox"
              name={field.name}
              checked={formData[field.name] || false}
              onChange={handleChange}
              disabled={loading}
            />
          ) : (
            <input
              id={field.name}
              type={field.type || 'text'}
              name={field.name}
              value={formData[field.name] || ''}
              onChange={handleChange}
              placeholder={field.placeholder}
              disabled={loading}
              required={field.required}
            />
          )}

          {errors[field.name] && (
            <span className="error">{errors[field.name]}</span>
          )}
        </div>
      ))}

      <div className="form-actions">
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Saving...' : 'Save'}
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onCancel}
          disabled={loading}
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
