import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as academicService from '../../../../services/academicService';
import toast from 'react-hot-toast';
import './AcademicStructure.css';

export default function AcademicStructure() {
  const [showForm, setShowForm] = useState(false);
  const [structureType, setStructureType] = useState('faculties');
  const [serverErrors, setServerErrors] = useState({});

  const fetchStructure = useCallback(() => {
    switch (structureType) {
      case 'faculties': return academicService.getFaculties();
      case 'departments': return academicService.getDepartments();
      case 'programs': return academicService.getPrograms();
      default: return Promise.resolve([]);
    }
  }, [structureType]);
  const { data: resp, loading, refresh } = useApi(fetchStructure, [structureType]);
  const structure = resp?.results || resp || [];

  const handleSave = async (formData) => {
    try {
      const service = structureType === 'faculties' ? 'createFaculty' : 'createDepartment';
      await academicService[service](formData);
      toast.success('Structure item created');
      setShowForm(false);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to save structure');
    }
  };

  return (
    <div className="academic-structure">
      <div className="header">
        <h1>Academic Structure</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          Add Item
        </button>
      </div>

      <div className="type-selector">
        <select value={structureType} onChange={(e) => setStructureType(e.target.value)}>
          <option value="faculties">Faculties</option>
          <option value="departments">Departments</option>
          <option value="programs">Programs</option>
          <option value="courses">Courses</option>
        </select>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            fields={[
              { name: 'code', label: 'Code', type: 'text', required: true },
              { name: 'name', label: 'Name', type: 'text', required: true },
              { name: 'description', label: 'Description', type: 'textarea' }
            ]}
            onSubmit={handleSave}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      <Table
        data={structure}
        columns={[
          { key: 'code', label: 'Code' },
          { key: 'name', label: 'Name' },
          { key: 'description', label: 'Description' },
          { key: 'status', label: 'Status' }
        ]}
        loading={loading}
      />
    </div>
  );
}
