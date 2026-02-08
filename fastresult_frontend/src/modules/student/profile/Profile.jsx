import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import './Profile.css';
import useApi from '../../../../hooks/useApi';
import * as userService from '../../../../services/userService';
import { useAuth } from '../../../../hooks/useAuth';
import toast from 'react-hot-toast';

export default function StudentProfile() {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  const fetchProfile = useCallback(() => user?.id ? userService.getUser(user.id) : Promise.resolve(null), [user?.id]);
  const { data: profile, loading: isLoading, error, refresh: refreshProfile } = useApi(fetchProfile, [user?.id]);

  const handleUpdateProfile = async (data) => {
    if (!user?.id) return;
    try {
      setServerErrors({});
      await userService.updateUser(user.id, data);
      toast.success('Profile updated');
      setIsEditing(false);
      await refreshProfile();
    } catch (err) {
      if (err.response?.data) {
        setServerErrors(err.response.data);
      } else {
        toast.error('Failed to update profile');
      }
    }
  };

  if (isLoading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Failed to load profile</div>;

  return (
    <div className="student-profile">
      <h1>My Profile</h1>
      
      {isEditing ? (
        <Form
          fields={[
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'email', label: 'Email', type: 'email', required: true },
            { name: 'phone', label: 'Phone', type: 'text' },
            { name: 'address', label: 'Address', type: 'text' }
          ]}
          initialData={profile}
          onSubmit={handleUpdateProfile}
          onCancel={() => { setIsEditing(false); setServerErrors({}); }}
          serverErrors={serverErrors}
        />
      ) : (
        <div className="profile-view">
          {profile && (
            <>
              <div className="profile-field">
                <label>Full Name:</label>
                <p>{profile.first_name} {profile.last_name}</p>
              </div>
              <div className="profile-field">
                <label>Email:</label>
                <p>{profile.email}</p>
              </div>
              <div className="profile-field">
                <label>Phone:</label>
                <p>{profile.phone || 'Not provided'}</p>
              </div>
              <div className="profile-field">
                <label>Status:</label>
                <p>{profile.is_active ? 'Active' : 'Inactive'}</p>
              </div>
              <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
                Edit Profile
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
