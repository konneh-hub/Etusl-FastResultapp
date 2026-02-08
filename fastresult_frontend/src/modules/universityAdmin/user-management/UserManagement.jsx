import React, { useState, useMemo, useCallback } from 'react';
import CRUDTable from '../../../../components/CRUDTable/CRUDTable';
import Form from '../../../../components/Form/Form';
import './UserManagement.css';
import useApi from '../../../../hooks/useApi';
import * as userService from '../../../../services/userService';
import * as academicService from '../../../../services/academicService';
import authService from '../../../../services/auth.service';
import toast from 'react-hot-toast';

export default function UserManagement() {
  const currentUser = authService.getCurrentUser();
  const scope = useMemo(() => ({
    university: currentUser?.university || currentUser?.university_id || currentUser?.universityId
  }), [currentUser]);

  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [serverErrors, setServerErrors] = useState({});

  const fetchUsers = useCallback(() => userService.getUsers({ page, pageSize: limit, search, filters: scope }), [page, limit, search, scope]);
  const { data: usersResp, loading: loadingUsers, error: usersError, refresh: refreshUsers } = useApi(fetchUsers, [page, limit, search, scope]);

  const fetchDepartments = useCallback(() => academicService.getDepartments({ universityId: scope.university }), [scope]);
  const { data: departmentsResp } = useApi(fetchDepartments, [scope]);

  const fetchRoles = useCallback(() => userService.getRoles(), []);
  const { data: rolesResp } = useApi(fetchRoles, []);

  const users = usersResp?.results || [];
  const pagination = usersResp ? { current: usersResp.page || page, total: usersResp.count || usersResp.total || 0, limit } : null;

  const handleCreateOrUpdate = async (formData) => {
    try {
      setServerErrors({});
      if (editingUser && editingUser.id) {
        await userService.updateUser(editingUser.id, formData);
        toast.success('User updated');
      } else {
        await userService.createUser(formData);
        toast.success('User created');
      }
      setShowForm(false);
      setEditingUser(null);
      await refreshUsers();
    } catch (err) {
      if (err.response?.data) {
        setServerErrors(err.response.data);
      } else {
        toast.error('Failed to save user');
      }
    }
  };

  const handleDelete = async (row) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      await userService.deleteUser(row.id);
      toast.success('User deleted');
      await refreshUsers();
    } catch (err) {
      toast.error('Failed to delete user');
    }
  };

  const columns = [
    { key: 'first_name', label: 'First Name' },
    { key: 'last_name', label: 'Last Name' },
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Role' },
    { key: 'is_active', label: 'Active' }
  ];

  const formFields = [
    { name: 'first_name', label: 'First Name', type: 'text', required: true },
    { name: 'last_name', label: 'Last Name', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'role', label: 'Role', type: 'select', required: true, options: (rolesResp || []).map(r => ({ value: r.id || r.code || r.name, label: r.name })) },
    { name: 'department', label: 'Department', type: 'select', options: (departmentsResp?.results || departmentsResp || []).map(d => ({ value: d.id, label: d.name })) }
  ];

  return (
    <div className="user-management">
      <div className="header">
        <h1>User Management</h1>
        <button className="btn btn-primary" onClick={() => { setEditingUser(null); setServerErrors({}); setShowForm(true); }}>
          Add User
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            title={editingUser ? 'Edit User' : 'Create User'}
            fields={formFields}
            initialData={editingUser}
            onSubmit={handleCreateOrUpdate}
            onCancel={() => { setShowForm(false); setEditingUser(null); setServerErrors({}); }}
            isLoading={false}
            serverErrors={serverErrors}
          />
        </div>
      )}

      <CRUDTable
        title="Users"
        columns={columns}
        data={users}
        loading={loadingUsers}
        pagination={pagination}
        onPageChange={(p) => setPage(p)}
        onAdd={() => { setEditingUser(null); setServerErrors({}); setShowForm(true); }}
        onEdit={(row) => { setEditingUser(row); setServerErrors({}); setShowForm(true); }}
        onDelete={handleDelete}
      />
    </div>
  );
}
