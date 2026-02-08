import React, { useState } from 'react';
import Form from '../../../../components/Form/Form';
import * as authService from '../../../../services/authService';
import toast from 'react-hot-toast';
import './ResetPassword.css';

export default function ResetPassword() {
  const [isLoading, setIsLoading] = useState(false);
  const [resetComplete, setResetComplete] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  const handleResetPassword = async (data) => {
    try {
      setIsLoading(true);
      await authService.resetPassword(data);
      toast.success('Password reset successfully');
      setResetComplete(true);
      setServerErrors({});
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };

  if (resetComplete) {
    return (
      <div className="reset-password">
        <div className="reset-container">
          <div className="success-message">
            <h1>✓ Password Reset Successfully</h1>
            <p>Your password has been reset. You can now login with your new password.</p>
            <a href="/login" className="btn btn-primary">
              Login
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="reset-password">
      <div className="reset-container">
        <h1>Reset Your Password</h1>
        <p>Enter your new password below</p>

        <Form
          fields={[
            { name: 'password', label: 'New Password', type: 'password', required: true },
            { name: 'confirmPassword', label: 'Confirm Password', type: 'password', required: true }
          ]}
          onSubmit={handleResetPassword}
        />

        <a href="/forgot-password" className="btn-link">Back to Forgot Password</a>
      </div>
    </div>
  );
}
