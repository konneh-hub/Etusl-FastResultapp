import React, { useState, useEffect } from 'react';
import adminService from '../../../../services/admin.service';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import './Users.css';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [pagination, setPagination] = useState({ offset: 0, limit: 20 });

  const roleOptions = [
    { value: 'student', label: 'Student' },
    { value: 'lecturer', label: 'Lecturer' },
    { value: 'hod', label: 'HOD' },
    { value: 'exam_officer', label: 'Exam Officer' },
    { value: 'dean', label: 'Dean' },
    { value: 'university_admin', label: 'University Admin' }
  ];

  // Load users on component mount and when filters change
  useEffect(() => {
    loadUsers();
  }, [search, roleFilter, pagination.offset]);

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      const response = await adminService.listUsers({
        search,
        role: roleFilter,
        ...pagination
      });
      setUsers(response.results || []);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateUser = () => {
    setEditingUser(null);
    setShowForm(true);
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setShowForm(true);
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await adminService.deleteUser(userId);
        loadUsers();
      } catch (error) {
        console.error('Failed to delete user:', error);
      }
    }
  };

  const handleSubmitForm = async (formData) => {
    try {
      setIsLoading(true);
      if (editingUser) {
        await adminService.updateUser(editingUser.id, formData);
      } else {
        await adminService.createUser(formData);
      }
      setShowForm(false);
      loadUsers();
    } catch (error) {
      console.error('Failed to submit form:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formFields = [
    {
      name: 'email',
      label: 'Email',
      type: 'email',
      required: true,
      disabled: editingUser ? true : false
    },
    {
      name: 'first_name',
      label: 'First Name',
      type: 'text',
      required: true
    },
    {
      name: 'last_name',
      label: 'Last Name',
      type: 'text',
      required: true
    },
    {
      name: 'role',
      label: 'Role',
      type: 'select',
      required: true,
      options: roleOptions
    },
    {
      name: 'password',
      label: 'Password',
      type: 'password',
      required: !editingUser,
      minLength: 8
    },
    {
      name: 'is_active',
      label: 'Active',
      type: 'checkbox'
    }
  ];

  const tableColumns = [
    { key: 'email', label: 'Email' },
    { key: 'first_name', label: 'First Name' },
    { key: 'last_name', label: 'Last Name' },
    { key: 'role', label: 'Role' },
    { key: 'is_active', label: 'Status', render: (value) => value ? 'Active' : 'Inactive' }
  ];

  const tableActions = [
    { label: 'Edit', onClick: handleEditUser, variant: 'secondary' },
    { label: 'Delete', onClick: handleDeleteUser, variant: 'danger' }
  ];

  return (
    <div className="users-container">
      <div className="users-header">
        <h1>User Management</h1>
        <button onClick={handleCreateUser} className="btn btn-primary">
          + New User
        </button>
      </div>

      <div className="users-filters">
        <input
          type="text"
          placeholder="Search by email or name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="filter-input"
        />
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="filter-select"
        >
          <option value="">All Roles</option>
          {roleOptions.map((role) => (
            <option key={role.value} value={role.value}>
              {role.label}
            </option>
          ))}
        </select>
      </div>

      {isLoading && !showForm ? (
        <div className="loading">Loading users...</div>
      ) : (
        <Table
          columns={tableColumns}
          data={users}
          actions={tableActions}
          isLoading={isLoading}
        />
      )}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <Form
              title={editingUser ? 'Edit User' : 'New User'}
              fields={formFields}
              initialData={editingUser || {}}
              onSubmit={handleSubmitForm}
              onCancel={() => setShowForm(false)}
              submitText={editingUser ? 'Update' : 'Create'}
              isLoading={isLoading}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Users;
