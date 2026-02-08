import React from 'react'

export default function Button({ 
  children, 
  type = 'button', 
  variant = 'primary', 
  size = 'md',
  disabled = false,
  ...props 
}) {
  const classes = `btn btn-${variant} btn-${size} ${disabled ? 'disabled' : ''}`
  
  return (
    <button 
      type={type} 
      className={classes}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}
