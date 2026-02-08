import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as messagingService from '../../../../services/messagingService';
import toast from 'react-hot-toast';
import './Communication.css';

export default function Communication() {
  const [showForm, setShowForm] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  const fetchMessages = useCallback(() => messagingService.getMessages(), []);
  const { data: resp, loading, refresh } = useApi(fetchMessages, []);
  const messages = resp?.results || resp || [];

  const handleSendMessage = async (messageData) => {
    try {
      await messagingService.createMessage(messageData);
      toast.success('Message sent');
      setShowForm(false);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to send message');
    }
  };

  return (
    <div className="admin-communication">
      <div className="header">
        <h1>Communication</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          Send Message
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            fields={[
              { name: 'recipient', label: 'Recipient', type: 'select', required: true },
              { name: 'subject', label: 'Subject', type: 'text', required: true },
              { name: 'message', label: 'Message', type: 'textarea', required: true }
            ]}
            onSubmit={handleSendMessage}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      <Table
        data={messages}
        columns={[
          { key: 'recipient', label: 'Recipient' },
          { key: 'subject', label: 'Subject' },
          { key: 'date', label: 'Date' },
          { key: 'status', label: 'Status' }
        ]}
        loading={isLoading}
      />
    </div>
  );
}
