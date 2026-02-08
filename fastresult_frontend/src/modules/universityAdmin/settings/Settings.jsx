import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import useApi from '../../../../hooks/useApi';
import toast from 'react-hot-toast';
import './Settings.css';

export default function Settings() {
  const [isEditing, setIsEditing] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  // Placeholder for settings service - can be created if needed
  const fetchSettings = useCallback(async () => {
    return { general: {}, academic: {}, notification: {} };
  }, []);
  const { data: settings, loading, refresh } = useApi(fetchSettings, []);

  const handleSaveSettings = async (formData) => {
    try {
      // TODO: Implement settings update via API call
      toast.success('Settings saved');
      setIsEditing(false);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to save settings');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="settings">
      <div className="header">
        <h1>University Settings</h1>
        {!isEditing && (
          <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
            Edit Settings
          </button>
        )}
      </div>

      {isEditing ? (
        <Form
          fields={[
            { name: 'universityName', label: 'University Name', type: 'text' },
            { name: 'academicYear', label: 'Academic Year', type: 'text' },
            { name: 'gradeScale', label: 'Grade Scale', type: 'select' },
            { name: 'resultReleaseDate', label: 'Result Release Date', type: 'date' }
          ]}
          initialData={settings}
          onSubmit={handleSaveSettings}
          onCancel={() => setIsEditing(false)}
        />
      ) : (
        <div className="settings-view">
          <div className="settings-group">
            <h2>General Settings</h2>
            {settings && (
              <>
                <div className="setting-item">
                  <label>University Name:</label>
                  <p>{settings.universityName}</p>
                </div>
                <div className="setting-item">
                  <label>Academic Year:</label>
                  <p>{settings.academicYear}</p>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
