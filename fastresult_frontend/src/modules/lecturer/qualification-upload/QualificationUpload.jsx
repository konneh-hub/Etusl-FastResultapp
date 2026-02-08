import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as filesService from '../../../../services/filesService';
import toast from 'react-hot-toast';
import './QualificationUpload.css';

export default function QualificationUpload() {
  const [showForm, setShowForm] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  const fetchQualifications = useCallback(() => filesService.getQualifications ? filesService.getQualifications() : Promise.resolve([]), []);
  const { data: resp, loading, refresh } = useApi(fetchQualifications, []);
  const qualifications = resp?.results || resp || [];

  const handleUploadQualification = async (formData) => {
    try {
      const formDataObj = new FormData();
      Object.keys(formData).forEach(key => {
        formDataObj.append(key, formData[key]);
      });
      await filesService.uploadFile(formDataObj);
      toast.success('Qualification uploaded');
      setShowForm(false);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to upload qualification');
    }
  };

  return (
    <div className="qualification-upload">
      <div className="header">
        <h1>Qualifications</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          Add Qualification
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            fields={[
              { name: 'degree', label: 'Degree', type: 'text', required: true },
              { name: 'field', label: 'Field of Study', type: 'text', required: true },
              { name: 'institution', label: 'Institution', type: 'text', required: true },
              { name: 'year', label: 'Year', type: 'number', required: true },
              { name: 'certificate', label: 'Certificate', type: 'file', required: true }
            ]}
            onSubmit={handleUploadQualification}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      <Table
        data={qualifications}
        columns={[
          { key: 'degree', label: 'Degree' },
          { key: 'field', label: 'Field' },
          { key: 'institution', label: 'Institution' },
          { key: 'year', label: 'Year' }
        ]}
        loading={loading}
      />
    </div>
  );
}
