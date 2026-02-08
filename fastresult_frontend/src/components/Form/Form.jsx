import React, { useState } from 'react';
import './Form.css';

/**
 * Generic Form Component with field configuration
 * Supports: textrules, select, textarea, checkbox, date, file, email, password
 */
const Form = ({
  title,
  fields,
  initialData = {},
  onSubmit,
  onCancel,
  submitText = 'Submit',
  isLoading = false,
  mode = 'create', // 'create' or 'edit'
  serverErrors = {} // { fieldName: ['error1','error2'] }
}) => {
  const [formData, setFormData] = useState(initialData);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  // Merge server-side validation errors into the form errors
  useEffect(() => {
    if (serverErrors && Object.keys(serverErrors).length) {
      const mapped = {};
      Object.keys(serverErrors).forEach((k) => {
        mapped[k] = Array.isArray(serverErrors[k]) ? serverErrors[k].join(' ') : String(serverErrors[k]);
      });
      setErrors((prev) => ({ ...prev, ...mapped }));
      // Mark fields as touched so errors are visible
      const touchedFields = Object.keys(mapped).reduce((acc, k) => ({ ...acc, [k]: true }), {});
      setTouched((prev) => ({ ...prev, ...touchedFields }));
    }
  }, [serverErrors]);

  const validateField = (name, value) => {
    const field = fields.find((f) => f.name === name);
    if (!field) return '';

    // Required validation
    if (field.required && !value) {
      return `${field.label} is required`;
    }

    // Email validation
    if (field.type === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        return 'Invalid email format';
      }
    }

    // Min length validation
    if (field.minLength && value.length < field.minLength) {
      return `Must be at least ${field.minLength} characters`;
    }

    // Max length validation
    if (field.maxLength && value.length > field.maxLength) {
      return `Must not exceed ${field.maxLength} characters`;
    }

    // Number validation
    if (field.type === 'number' && value) {
      if (isNaN(value)) return 'Must be a number';
      if (field.min !== undefined && Number(value) < field.min) {
        return `Must be at least ${field.min}`;
      }
      if (field.max !== undefined && Number(value) > field.max) {
        return `Must not exceed ${field.max}`;
      }
    }

    // Custom validation
    if (field.validate) {
      const customError = field.validate(value, formData);
      if (customError) return customError;
    }

    return '';
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;

    setFormData((prev) => ({
      ...prev,
      [name]: newValue
    }));

    // Validate on change
    if (touched[name]) {
      const error = validateField(name, newValue);
      setErrors((prev) => ({
        ...prev,
        [name]: error
      }));
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched((prev) => ({
      ...prev,
      [name]: true
    }));

    const error = validateField(name, value);
    setErrors((prev) => ({
      ...prev,
      [name]: error
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validate all fields
    const newErrors = {};
    let hasErrors = false;

    fields.forEach((field) => {
      const error = validateField(field.name, formData[field.name] || '');
      if (error) {
        newErrors[field.name] = error;
        hasErrors = true;
      }
    });

    setErrors(newErrors);

    if (!hasErrors) {
      onSubmit(formData);
    }
  };

  const renderField = (field) => {
    const value = formData[field.name] || '';
    const error = errors[field.name];
    const isTouched = touched[field.name];
    const hasError = error && isTouched;

    const fieldClassName = `form-field ${hasError ? 'form-field--error' : ''} ${
      field.className || ''
    }`;

    switch (field.type) {
      case 'text':
      case 'email':
      case 'password':
      case 'url':
      case 'tel':
        return (
          <div key={field.name} className={fieldClassName}>
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <input
              type={field.type}
              id={field.name}
              name={field.name}
              value={value}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder={field.placeholder}
              disabled={field.disabled || isLoading}
              className="form-input"
            />
            {hasError && <span className="form-error">{error}</span>}
          </div>
        );

      case 'number':
        return (
          <div key={field.name} className={fieldClassName}>
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <input
              type="number"
              id={field.name}
              name={field.name}
              value={value}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder={field.placeholder}
              min={field.min}
              max={field.max}
              step={field.step || '1'}
              disabled={field.disabled || isLoading}
              className="form-input"
            />
            {hasError && <span className="form-error">{error}</span>}
          </div>
        );

      case 'textarea':
        return (
          <div key={field.name} className={fieldClassName}>
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <textarea
              id={field.name}
              name={field.name}
              value={value}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder={field.placeholder}
              rows={field.rows || 4}
              disabled={field.disabled || isLoading}
              className="form-textarea"
            />
            {hasError && <span className="form-error">{error}</span>}
          </div>
        );

      case 'select':
        return (
          <div key={field.name} className={fieldClassName}>
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <select
              id={field.name}
              name={field.name}
              value={value}
              onChange={handleChange}
              onBlur={handleBlur}
              disabled={field.disabled || isLoading}
              className="form-select"
            >
              <option value="">{field.placeholder || 'Select an option'}</option>
              {field.options?.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {hasError && <span className="form-error">{error}</span>}
          </div>
        );

      case 'checkbox':
        return (
          <div key={field.name} className={`${fieldClassName} form-field--checkbox`}>
            <input
              type="checkbox"
              id={field.name}
              name={field.name}
              checked={value}
              onChange={handleChange}
              onBlur={handleBlur}
              disabled={field.disabled || isLoading}
              className="form-checkbox"
            />
            <label htmlFor={field.name} className="form-label form-label--inline">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            {hasError && <span className="form-error">{error}</span>}
          </div>
        );

      case 'date':
        return (
          <div key={field.name} className={fieldClassName}>
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <input
              type="date"
              id={field.name}
              name={field.name}
              value={value}
              onChange={handleChange}
              onBlur={handleBlur}
              disabled={field.disabled || isLoading}
              className="form-input"
            />
            {hasError && <span className="form-error">{error}</span>}
          </div>
        );

      case 'file':
        return (
          <div key={field.name} className={fieldClassName}>
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <input
              type="file"
              id={field.name}
              name={field.name}
              onChange={handleChange}
              onBlur={handleBlur}
              accept={field.accept}
              multiple={field.multiple}
              disabled={field.disabled || isLoading}
              className="form-input"
            />
            {hasError && <span className="form-error">{error}</span>}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="form-container">
      {title && <h2 className="form-title">{title}</h2>}
      <form onSubmit={handleSubmit} className="form">
        <div className="form-fields">
          {fields.map((field) => renderField(field))}
        </div>

        <div className="form-actions">
          <button
            type="submit"
            disabled={isLoading}
            className="btn btn-primary"
          >
            {isLoading ? 'Processing...' : submitText}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default Form;
