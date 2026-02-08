import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as messagingService from '../../../../services/messagingService';
import toast from 'react-hot-toast';
import './Announcements.css';

export default function Announcements() {
  const [showForm, setShowForm] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  const fetchAnnouncements = useCallback(() => messagingService.getAnnouncements(), []);
  const { data: resp, loading, refresh } = useApi(fetchAnnouncements, []);
  const announcements = resp?.results || resp || [];

  const handleCreateAnnouncement = async (formData) => {
    try {
      await messagingService.createAnnouncement(formData);
      toast.success('Announcement created');
      setShowForm(false);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to create announcement');
    }
  };

  return (
    <div className="announcements">
      <div className="header">
        <h1>Announcements</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          New Announcement
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            fields={[
              { name: 'title', label: 'Title', type: 'text', required: true },
              { name: 'content', label: 'Content', type: 'textarea', required: true },
              { name: 'targetAudience', label: 'Target Audience', type: 'select', required: true }
            ]}
            onSubmit={handleCreateAnnouncement}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      <Table
        data={announcements}
        columns={[
          { key: 'title', label: 'Title' },
          { key: 'audience', label: 'Audience' },
          { key: 'date', label: 'Date' },
          { key: 'status', label: 'Status' }
        ]}
        loading={loading}
      />
    </div>
  );
}
