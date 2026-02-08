import React, { useState, useMemo, useCallback } from 'react';
import CRUDTable from '../../../../components/CRUDTable/CRUDTable';
import Form from '../../../../components/Form/Form';
import './StudentManagement.css';
import useApi from '../../../../hooks/useApi';
import * as userService from '../../../../services/userService';
import * as academicService from '../../../../services/academicService';
import authService from '../../../../services/auth.service';
import toast from 'react-hot-toast';

export default function StudentManagement() {
  const currentUser = authService.getCurrentUser();
  const scope = useMemo(() => ({
    university: currentUser?.university || currentUser?.university_id || currentUser?.universityId
  }), [currentUser]);

  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  const [serverErrors, setServerErrors] = useState({});

  const fetchStudents = useCallback(
    () => userService.getUsers({ page, pageSize: limit, search, filters: { ...scope, role: 'student' } }),
    [page, limit, search, scope]
  );
  const { data: studentsResp, loading: loadingStudents, error: studentsError, refresh: refreshStudents } = useApi(fetchStudents, [page, limit, search, scope]);

  const fetchPrograms = useCallback(() => academicService.getPrograms({ universityId: scope.university }), [scope]);
  const { data: programsResp } = useApi(fetchPrograms, [scope]);

  const students = studentsResp?.results || [];
  const pagination = studentsResp ? { current: studentsResp.page || page, total: studentsResp.count || studentsResp.total || 0, limit } : null;

  const handleCreateOrUpdate = async (formData) => {
    try {
      setServerErrors({});
      const payload = { ...formData, role: 'student' };
      if (editingStudent && editingStudent.id) {
        await userService.updateUser(editingStudent.id, payload);
        toast.success('Student updated');
      } else {
        await userService.createUser(payload);
        toast.success('Student created');
      }
      setShowForm(false);
      setEditingStudent(null);
      await refreshStudents();
    } catch (err) {
      if (err.response?.data) {
        setServerErrors(err.response.data);
      } else {
        toast.error('Failed to save student');
      }
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm('Are you sure you want to delete this student?')) return;
    try {
      await userService.deleteUser(row.id);
      toast.success('Student deleted');
      await refreshStudents();
    } catch (err) {
      toast.error('Failed to delete student');
    }
  };

  const columns = [
    { key: 'first_name', label: 'First Name' },
    { key: 'last_name', label: 'Last Name' },
    { key: 'email', label: 'Email' },
    { key: 'matric_number', label: 'Matric Number' },
    { key: 'program', label: 'Program' }
  ];

  const formFields = [
    { name: 'first_name', label: 'First Name', type: 'text', required: true },
    { name: 'last_name', label: 'Last Name', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'matric_number', label: 'Matric Number', type: 'text', required: true },
    { name: 'program', label: 'Program', type: 'select', required: true, options: (programsResp?.results || programsResp || []).map(p => ({ value: p.id, label: p.name })) }
  ];

  return (
    <div className="student-management">
      <div className="header">
        <h1>Student Management</h1>
        <button className="btn btn-primary" onClick={() => { setEditingStudent(null); setServerErrors({}); setShowForm(true); }}>
          Add Student
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            title={editingStudent ? 'Edit Student' : 'Create Student'}
            fields={formFields}
            initialData={editingStudent}
            onSubmit={handleCreateOrUpdate}
            onCancel={() => { setShowForm(false); setEditingStudent(null); setServerErrors({}); }}
            isLoading={false}
            serverErrors={serverErrors}
          />
        </div>
      )}

      <CRUDTable
        title="Students"
        columns={columns}
        data={students}
        loading={loadingStudents}
        pagination={pagination}
        onPageChange={(p) => setPage(p)}
        onAdd={() => { setEditingStudent(null); setServerErrors({}); setShowForm(true); }}
        onEdit={(row) => { setEditingStudent(row); setServerErrors({}); setShowForm(true); }}
        onDelete={handleDelete}
      />
    </div>
  );
}
