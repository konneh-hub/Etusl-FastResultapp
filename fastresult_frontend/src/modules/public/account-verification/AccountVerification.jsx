import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Form from '../../../../components/Form/Form'
import { authService } from '../../../../services/authService'
import toast from 'react-hot-toast'
import './AccountVerification.css'

export default function AccountVerification() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [serverErrors, setServerErrors] = useState({})
  const [successMessage, setSuccessMessage] = useState('')

  const handleClaimAccount = async (data) => {
    try {
      setIsLoading(true)
      setServerErrors({})
      setSuccessMessage('')

      const response = await authService.claimAccount({
        student_id: data.student_id || undefined,
        staff_id: data.staff_id || undefined,
        email: data.email,
        date_of_birth: data.date_of_birth,
        password: data.password,
        password_confirm: data.password_confirm,
      })

      // Save token to localStorage
      if (response.token) {
        localStorage.setItem('token', response.token)
        localStorage.setItem('user', JSON.stringify(response.user))
        localStorage.setItem('role', response.role)
      }

      setSuccessMessage('Account activated successfully! Redirecting to login...')
      toast.success('Account activated! Redirecting...')

      // Redirect to dashboard after short delay
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } catch (error) {
      const errors = error.response?.data || {}
      setServerErrors(errors)
      
      // Handle different error scenarios
      if (errors.non_field_errors) {
        toast.error(errors.non_field_errors[0])
      } else if (errors.student_id || errors.staff_id) {
        toast.error('Student/Staff ID not found in our records')
      } else if (errors.email) {
        toast.error('Email does not match our records')
      } else if (errors.date_of_birth) {
        toast.error('Date of birth does not match our records')
      } else if (errors.password) {
        toast.error('Passwords do not match')
      } else {
        toast.error(Object.values(errors)[0] || 'Account activation failed')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const fields = [
    {
      name: 'account_type',
      label: 'Account Type',
      type: 'select',
      options: [
        { label: 'Select account type', value: '' },
        { label: 'Student', value: 'student' },
        { label: 'Lecturer', value: 'lecturer' },
      ],
      required: true,
      dependents: ['id_field'],
    },
    {
      name: 'student_id',
      label: 'Student ID',
      type: 'text',
      placeholder: 'Enter your student ID',
      required: false,
      visible: (data) => data.account_type === 'student',
    },
    {
      name: 'staff_id',
      label: 'Staff ID',
      type: 'text',
      placeholder: 'Enter your staff ID',
      required: false,
      visible: (data) => data.account_type === 'lecturer',
    },
    {
      name: 'email',
      label: 'Email Address',
      type: 'email',
      placeholder: 'your.email@university.edu',
      required: true,
    },
    {
      name: 'date_of_birth',
      label: 'Date of Birth',
      type: 'date',
      required: true,
    },
    {
      name: 'password',
      label: 'Password',
      type: 'password',
      placeholder: 'Minimum 8 characters',
      required: true,
    },
    {
      name: 'password_confirm',
      label: 'Confirm Password',
      type: 'password',
      placeholder: 'Re-enter your password',
      required: true,
    },
  ]

  return (
    <div className="account-verification">
      <div className="verification-container">
        <h1>Activate Your Account</h1>
        <p className="subtitle">
          Your account has been pre-registered. Complete the activation to get started.
        </p>

        {successMessage && (
          <div className="success-message">
            <p>✓ {successMessage}</p>
          </div>
        )}

        {!successMessage && (
          <>
            <Form
              fields={fields}
              onSubmit={handleClaimAccount}
              isLoading={isLoading}
              serverErrors={serverErrors}
              submitButtonLabel="Activate Account"
              submitButtonClass="btn btn-primary btn-block"
            />

            <div className="login-link">
              <p>
                Already have an active account?{' '}
                <a href="/login">Go to login</a>
              </p>
            </div>

            <div className="help-section">
              <p className="help-text">
                Don't have a pre-registered account?{' '}
                <a href="#contact-admin">Contact your University Admin</a>
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

