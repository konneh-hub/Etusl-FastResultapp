import React, { useState, useMemo, useCallback } from 'react';
import CRUDTable from '../../../../components/CRUDTable/CRUDTable';
import Form from '../../../../components/Form/Form';
import './LecturerManagement.css';
import useApi from '../../../../hooks/useApi';
import * as userService from '../../../../services/userService';
import * as academicService from '../../../../services/academicService';
import authService from '../../../../services/auth.service';
import toast from 'react-hot-toast';

export default function LecturerManagement() {
  const currentUser = authService.getCurrentUser();
  const scope = useMemo(() => ({
    university: currentUser?.university || currentUser?.university_id || currentUser?.universityId
  }), [currentUser]);

  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingLecturer, setEditingLecturer] = useState(null);
  const [serverErrors, setServerErrors] = useState({});

  const fetchLecturers = useCallback(
    () => userService.getUsers({ page, pageSize: limit, search, filters: { ...scope, role: 'lecturer' } }),
    [page, limit, search, scope]
  );
  const { data: lecturersResp, loading: loadingLecturers, error: lecturersError, refresh: refreshLecturers } = useApi(fetchLecturers, [page, limit, search, scope]);

  const fetchDepartments = useCallback(() => academicService.getDepartments({ universityId: scope.university }), [scope]);
  const { data: departmentsResp } = useApi(fetchDepartments, [scope]);

  const lecturers = lecturersResp?.results || [];
  const pagination = lecturersResp ? { current: lecturersResp.page || page, total: lecturersResp.count || lecturersResp.total || 0, limit } : null;

  const handleCreateOrUpdate = async (formData) => {
    try {
      setServerErrors({});
      const payload = { ...formData, role: 'lecturer' };
      if (editingLecturer && editingLecturer.id) {
        await userService.updateUser(editingLecturer.id, payload);
        toast.success('Lecturer updated');
      } else {
        await userService.createUser(payload);
        toast.success('Lecturer created');
      }
      setShowForm(false);
      setEditingLecturer(null);
      await refreshLecturers();
    } catch (err) {
      if (err.response?.data) {
        setServerErrors(err.response.data);
      } else {
        toast.error('Failed to save lecturer');
      }
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm('Are you sure you want to delete this lecturer?')) return;
    try {
      await userService.deleteUser(row.id);
      toast.success('Lecturer deleted');
      await refreshLecturers();
    } catch (err) {
      toast.error('Failed to delete lecturer');
    }
  };

  const columns = [
    { key: 'first_name', label: 'First Name' },
    { key: 'last_name', label: 'Last Name' },
    { key: 'email', label: 'Email' },
    { key: 'department', label: 'Department' }
  ];

  const formFields = [
    { name: 'first_name', label: 'First Name', type: 'text', required: true },
    { name: 'last_name', label: 'Last Name', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'phone', label: 'Phone', type: 'text' },
    { name: 'department', label: 'Department', type: 'select', required: true, options: (departmentsResp?.results || departmentsResp || []).map(d => ({ value: d.id, label: d.name })) }
  ];

  return (
    <div className="lecturer-management">
      <div className="header">
        <h1>Lecturer Management</h1>
        <button className="btn btn-primary" onClick={() => { setEditingLecturer(null); setServerErrors({}); setShowForm(true); }}>
          Add Lecturer
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            title={editingLecturer ? 'Edit Lecturer' : 'Create Lecturer'}
            fields={formFields}
            initialData={editingLecturer}
            onSubmit={handleCreateOrUpdate}
            onCancel={() => { setShowForm(false); setEditingLecturer(null); setServerErrors({}); }}
            isLoading={false}
            serverErrors={serverErrors}
          />
        </div>
      )}

      <CRUDTable
        title="Lecturers"
        columns={columns}
        data={lecturers}
        loading={loadingLecturers}
        pagination={pagination}
        onPageChange={(p) => setPage(p)}
        onAdd={() => { setEditingLecturer(null); setServerErrors({}); setShowForm(true); }}
        onEdit={(row) => { setEditingLecturer(row); setServerErrors({}); setShowForm(true); }}
        onDelete={handleDelete}
      />
    </div>
  );
}
