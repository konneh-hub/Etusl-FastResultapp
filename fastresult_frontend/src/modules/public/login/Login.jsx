import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { authService } from '../../services/authService'
import Form from '../../components/ui/Form'
import './Login.css'

export default function Login() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [serverErrors, setServerErrors] = useState({})

  const handleLogin = useCallback(async (formData) => {
    try {
      setIsLoading(true)
      setServerErrors({})

      // Call login API with email and password
      const response = await authService.login(formData.email, formData.password)
      
      // Store token securely
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      localStorage.setItem('role', response.data.role)

      // Show success message
      toast.success('Login successful. Redirecting...')

      // Redirect to role-based dashboard
      const dashboardRoute = response.data.dashboard_route || '/dashboard'
      setTimeout(() => {
        navigate(dashboardRoute)
      }, 500)
    } catch (error) {
      const errorData = error.response?.data || {}
      
      // Handle different error scenarios
      if (errorData.error) {
        toast.error(errorData.error)
      } else if (errorData.non_field_errors) {
        toast.error(errorData.non_field_errors[0])
      } else if (errorData.email) {
        setServerErrors({ email: errorData.email[0] || 'Invalid email' })
        toast.error('Email is invalid')
      } else if (errorData.password) {
        setServerErrors({ password: errorData.password[0] || 'Invalid password' })
        toast.error('Password is invalid')
      } else {
        toast.error('Login failed. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }, [navigate])

  const fields = [
    {
      name: 'email',
      label: 'Email Address',
      type: 'email',
      placeholder: 'your.email@university.edu',
      required: true,
      autoComplete: 'email',
    },
    {
      name: 'password',
      label: 'Password',
      type: 'password',
      placeholder: 'Enter your password',
      required: true,
      autoComplete: 'current-password',
    },
  ]

  return (
    <div className="login">
      <div className="login-container">
        <div className="login-card">
          <h1>Fast Result</h1>
          <p className="subtitle">Student Result Management System</p>

          <Form
            fields={fields}
            onSubmit={handleLogin}
            isLoading={isLoading}
            serverErrors={serverErrors}
            submitLabel="Login"
          />

          <div className="login-footer">
            <p className="help-text">
              Don't have an account?{' '}
              <a href="/account-verification">
                Activate your preloaded account
              </a>
            </p>
            <p className="help-text">
              <a href="/forgot-password">Forgot your password?</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
