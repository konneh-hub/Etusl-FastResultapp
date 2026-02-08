import React, { useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import Badge from '../../../../components/Badge/Badge';
import useApi from '../../../../hooks/useApi';
import * as notificationService from '../../../../services/notificationService';
import toast from 'react-hot-toast';
import './Notifications.css';

export default function Notifications() {
  const fetchNotifications = useCallback(() => notificationService.getNotifications(), []);
  const { data: resp, loading, refresh } = useApi(fetchNotifications, []);
  const notifications = resp?.results || resp || [];

  const handleMarkRead = async (notificationId) => {
    try {
      await notificationService.markNotificationAsRead(notificationId);
      toast.success('Marked as read');
      await refresh();
    } catch (error) {
      toast.error('Failed to mark as read');
    }
  };

  return (
    <div className="notifications">
      <h1>Notifications</h1>

      <Table
        data={notifications}
        columns={[
          { key: 'title', label: 'Title' },
          { key: 'message', label: 'Message' },
          { key: 'type', label: 'Type' },
          { key: 'date', label: 'Date' },
          { key: 'read', label: 'Status', render: (read) => <Badge status={read ? 'read' : 'unread'} /> },
          { key: 'actions', label: 'Actions', render: (_, row) => (
            !row.read && <button onClick={() => handleMarkRead(row.id)}>Mark as Read</button>
          )}
        ]}
        loading={loading}
      />
    </div>
  );
}
