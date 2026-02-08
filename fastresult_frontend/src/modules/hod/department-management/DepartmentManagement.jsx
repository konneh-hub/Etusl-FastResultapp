import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as academicService from '../../../../services/academicService';
import toast from 'react-hot-toast';
import './DepartmentManagement.css';

export default function DepartmentManagement() {
  const [showForm, setShowForm] = useState(false);
  const [editingDept, setEditingDept] = useState(null);
  const [serverErrors, setServerErrors] = useState({});

  const fetchDepartments = useCallback(() => academicService.getDepartments(), []);
  const { data: resp, loading, refresh } = useApi(fetchDepartments, []);
  const departments = resp?.results || resp || [];

  const handleSaveDepartment = async (formData) => {
    try {
      if (editingDept?.id) {
        await academicService.updateDepartment(editingDept.id, formData);
        toast.success('Department updated');
      } else {
        await academicService.createDepartment(formData);
        toast.success('Department created');
      }
      setShowForm(false);
      setEditingDept(null);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to save department');
    }
  };

  return (
    <div className="department-management">
      <div className="header">
        <h1>Department Management</h1>
        <button className="btn btn-primary" onClick={() => { setEditingDept(null); setShowForm(true); }}>
          Add Department
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            fields={[
              { name: 'code', label: 'Department Code', type: 'text', required: true },
              { name: 'name', label: 'Department Name', type: 'text', required: true },
              { name: 'description', label: 'Description', type: 'textarea' },
              { name: 'head', label: 'Department Head', type: 'select', required: true }
            ]}
            initialData={editingDept}
            onSubmit={handleSaveDepartment}
            onCancel={() => { setShowForm(false); setEditingDept(null); }}
          />
        </div>
      )}

      <Table
        data={departments}
        columns={[
          { key: 'code', label: 'Code' },
          { key: 'name', label: 'Name' },
          { key: 'head', label: 'Head' },
          { key: 'actions', label: 'Actions', render: (_, row) => (
            <div>
              <button onClick={() => { setEditingDept(row); setShowForm(true); }}>Edit</button>
            </div>
          )}
        ]}
        loading={loading}
      />
    </div>
  );
}
