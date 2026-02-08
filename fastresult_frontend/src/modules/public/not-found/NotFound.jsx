import React from 'react';
import './NotFound.css';

export default function NotFound() {
  return (
    <div className="not-found">
      <div className="error-container">
        <h1>Page Not Found</h1>
        <p className="error-code">404</p>
        <p className="error-message">Sorry, the page you're looking for doesn't exist.</p>
        <div className="actions">
          <button className="btn btn-primary" onClick={() => window.history.back()}>
            Go Back
          </button>
          <a href="/" className="btn btn-secondary">
            Go to Home
          </a>
        </div>
      </div>
    </div>
  );
}
