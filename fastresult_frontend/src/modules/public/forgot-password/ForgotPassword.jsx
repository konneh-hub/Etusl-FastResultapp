import React, { useState } from 'react';
import Form from '../../../../components/Form/Form';
import * as authService from '../../../../services/authService';
import toast from 'react-hot-toast';
import './ForgotPassword.css';

export default function ForgotPassword() {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  const handleRequestReset = async (data) => {
    try {
      setIsLoading(true);
      await authService.requestPasswordReset(data.email);
      setEmail(data.email);
      setStep(2);
      toast.success('Reset code sent to your email');
      setServerErrors({});
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to request reset');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyCode = async (data) => {
    try {
      setIsLoading(true);
      await authService.verifyResetCode({ email, code: data.code });
      setStep(3);
      toast.success('Code verified');
      setServerErrors({});
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Invalid code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (data) => {
    try {
      setIsLoading(true);
      await authService.resetPassword({ email, password: data.password });
      toast.success('Password reset successfully');
      window.location.href = '/login';
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="forgot-password">
      <div className="reset-container">
        <h1>Reset Your Password</h1>

        {step === 1 && (
          <>
            <p>Enter your email address and we'll send you a link to reset your password.</p>
            <Form
              fields={[
                { name: 'email', label: 'Email Address', type: 'email', required: true }
              ]}
              onSubmit={handleRequestReset}
            />
          </>
        )}

        {step === 2 && (
          <>
            <p>We've sent a verification code to {email}.</p>
            <Form
              fields={[
                { name: 'code', label: 'Verification Code', type: 'text', required: true }
              ]}
              onSubmit={handleVerifyCode}
            />
          </>
        )}

        {step === 3 && (
          <>
            <p>Create your new password</p>
            <Form
              fields={[
                { name: 'password', label: 'New Password', type: 'password', required: true },
                { name: 'confirmPassword', label: 'Confirm Password', type: 'password', required: true }
              ]}
              onSubmit={handleResetPassword}
            />
          </>
        )}

        <a href="/login" className="btn-link">Back to Login</a>
      </div>
    </div>
  );
}
