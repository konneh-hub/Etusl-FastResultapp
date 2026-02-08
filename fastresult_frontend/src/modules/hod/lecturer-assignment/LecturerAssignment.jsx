import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as courseService from '../../../../services/courseService';
import toast from 'react-hot-toast';
import './LecturerAssignment.css';

export default function LecturerAssignment() {
  const [showForm, setShowForm] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  const fetchAssignments = useCallback(() => courseService.getCourses(), []);
  const { data: resp, loading, refresh } = useApi(fetchAssignments, []);
  const assignments = resp?.results || resp || [];

  const handleCreateAssignment = async (formData) => {
    try {
      await courseService.assignLecturer(formData);
      toast.success('Lecturer assigned');
      setShowForm(false);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to assign lecturer');
    }
  };

  const handleRemoveAssignment = async (assignmentId) => {
    try {
      await courseService.deleteCourse(assignmentId);
      toast.success('Assignment removed');
      await refresh();
    } catch (error) {
      toast.error('Failed to remove assignment');
    }
  };

  return (
    <div className="lecturer-assignment">
      <div className="header">
        <h1>Lecturer Assignment</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          Assign Lecturer
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            fields={[
              { name: 'lecturer', label: 'Lecturer', type: 'select', required: true },
              { name: 'course', label: 'Course', type: 'select', required: true },
              { name: 'semester', label: 'Semester', type: 'select', required: true }
            ]}
            onSubmit={handleCreateAssignment}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      <Table
        data={assignments}
        columns={[
          { key: 'lecturer', label: 'Lecturer' },
          { key: 'course', label: 'Course' },
          { key: 'semester', label: 'Semester' },
          { key: 'actions', label: 'Actions', render: (_, row) => (
            <button onClick={() => handleRemoveAssignment(row.id)}>Remove</button>
          )}
        ]}
        loading={loading}
      />
    </div>
  );
}
