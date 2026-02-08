import React, { useState, useEffect } from 'react';
import adminService from '../../../../services/admin.service';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import '../users/Users.css';

const Faculties = () => {
  const [faculties, setFaculties] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingFaculty, setEditingFaculty] = useState(null);
  const [search, setSearch] = useState('');
  const [pagination, setPagination] = useState({ offset: 0, limit: 20 });

  useEffect(() => {
    loadFaculties();
  }, [search, pagination.offset]);

  const loadFaculties = async () => {
    try {
      setIsLoading(true);
      const response = await adminService.listFaculties({
        search,
        ...pagination
      });
      setFaculties(response.results || []);
    } catch (error) {
      console.error('Failed to load faculties:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateFaculty = () => {
    setEditingFaculty(null);
    setShowForm(true);
  };

  const handleEditFaculty = (faculty) => {
    setEditingFaculty(faculty);
    setShowForm(true);
  };

  const handleDeleteFaculty = async (facultyId) => {
    if (window.confirm('Are you sure? This will affect all departments.')) {
      try {
        await adminService.deleteFaculty(facultyId);
        loadFaculties();
      } catch (error) {
        console.error('Failed to delete faculty:', error);
      }
    }
  };

  const handleSubmitForm = async (formData) => {
    try {
      setIsLoading(true);
      if (editingFaculty) {
        await adminService.updateFaculty(editingFaculty.id, formData);
      } else {
        await adminService.createFaculty(formData);
      }
      setShowForm(false);
      loadFaculties();
    } catch (error) {
      console.error('Failed to submit form:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formFields = [
    {
      name: 'name',
      label: 'Faculty Name',
      type: 'text',
      required: true,
      minLength: 3
    },
    {
      name: 'code',
      label: 'Faculty Code',
      type: 'text',
      required: true,
      maxLength: 10
    },
    {
      name: 'description',
      label: 'Description',
      type: 'textarea',
      rows: 4
    },
    {
      name: 'is_active',
      label: 'Active',
      type: 'checkbox'
    }
  ];

  const tableColumns = [
    { key: 'name', label: 'Faculty Name' },
    { key: 'code', label: 'Code' },
    { key: 'description', label: 'Description' },
    { key: 'is_active', label: 'Status', render: (value) => value ? 'Active' : 'Inactive' }
  ];

  const tableActions = [
    { label: 'Edit', onClick: handleEditFaculty, variant: 'secondary' },
    { label: 'Delete', onClick: handleDeleteFaculty, variant: 'danger' }
  ];

  return (
    <div className="users-container">
      <div className="users-header">
        <h1>Faculty Management</h1>
        <button onClick={handleCreateFaculty} className="btn btn-primary">+ New Faculty</button>
      </div>

      <div className="users-filters">
        <input
          type="text"
          placeholder="Search faculties..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="filter-input"
        />
      </div>

      {isLoading && !showForm ? (
        <div className="loading">Loading faculties...</div>
      ) : (
        <Table columns={tableColumns} data={faculties} actions={tableActions} isLoading={isLoading} />
      )}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <Form
              title={editingFaculty ? 'Edit Faculty' : 'New Faculty'}
              fields={formFields}
              initialData={editingFaculty || {}}
              onSubmit={handleSubmitForm}
              onCancel={() => setShowForm(false)}
              submitText={editingFaculty ? 'Update' : 'Create'}
              isLoading={isLoading}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Faculties;
