import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import Badge from '../../../../components/Badge/Badge';
import useApi from '../../../../hooks/useApi';
import * as courseService from '../../../../services/courseService';
import toast from 'react-hot-toast';
import './Registration.css';

export default function StudentRegistration() {
  const [showForm, setShowForm] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  const fetchRegistrations = useCallback(() => courseService.getCourses(), []);
  const { data: resp, loading, refresh } = useApi(fetchRegistrations, []);
  const registrations = resp?.results || resp || [];

  const handleRegister = async (formData) => {
    try {
      await courseService.createCourse(formData);
      toast.success('Registered for course');
      setShowForm(false);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to register');
    }
  };

  return (
    <div className="student-registration">
      <div className="header">
        <h1>Course Registration</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          Register Course
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            fields={[
              { name: 'course', label: 'Course', type: 'select', required: true },
              { name: 'semester', label: 'Semester', type: 'select', required: true }
            ]}
            onSubmit={handleRegister}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      <Table
        data={registrations}
        columns={[
          { key: 'courseCode', label: 'Course Code' },
          { key: 'courseTitle', label: 'Course Title' },
          { key: 'credits', label: 'Credits' },
          { key: 'semester', label: 'Semester' },
          { key: 'status', label: 'Status', render: (status) => <Badge status={status} /> }
        ]}
        loading={loading}
      />
    </div>
  );
}
