import React from 'react';
import './AccessDenied.css';

export default function AccessDenied() {
  return (
    <div className="access-denied">
      <div className="error-container">
        <h1>Access Denied</h1>
        <p className="error-code">403</p>
        <p className="error-message">Sorry, you don't have permission to access this page.</p>
        <div className="actions">
          <button className="btn btn-primary" onClick={() => window.history.back()}>
            Go Back
          </button>
          <a href="/dashboard" className="btn btn-secondary">
            Go to Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
