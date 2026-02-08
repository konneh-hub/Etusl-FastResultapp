import { forwardRef } from 'react'

/**
 * FormField: Reusable form input wrapper
 * Handles label, error message, required indicator
 */
const FormField = forwardRef(({
  label,
  type = 'text',
  placeholder,
  error,
  required = false,
  disabled = false,
  as = 'input',
  className = '',
  options = [],
  ...props
}, ref) => {
  const baseInputClass = `
    w-full px-3 py-2 border rounded-lg font-sm
    focus:outline-none focus:ring-2 focus:ring-blue-500
    transition-colors
    ${error ? 'border-red-500 bg-red-50' : 'border-gray-300'}
    ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
    ${className}
  `.trim()

  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {as === 'select' ? (
        <select
          ref={ref}
          className={baseInputClass}
          disabled={disabled}
          {...props}
        >
          <option value="">-- Select {label?.toLowerCase() || 'option'} --</option>
          {options.map(opt => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      ) : as === 'textarea' ? (
        <textarea
          ref={ref}
          className={baseInputClass}
          placeholder={placeholder}
          disabled={disabled}
          {...props}
        />
      ) : (
        <input
          ref={ref}
          type={type}
          className={baseInputClass}
          placeholder={placeholder}
          disabled={disabled}
          {...props}
        />
      )}

      {error && (
        <p className="text-red-500 text-xs mt-1">{error}</p>
      )}
    </div>
  )
})

FormField.displayName = 'FormField'

export default FormField
