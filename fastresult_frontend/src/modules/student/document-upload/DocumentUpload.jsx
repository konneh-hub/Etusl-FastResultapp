import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import Badge from '../../../../components/Badge/Badge';
import useApi from '../../../../hooks/useApi';
import * as filesService from '../../../../services/filesService';
import toast from 'react-hot-toast';
import './DocumentUpload.css';

export default function DocumentUpload() {
  const [showForm, setShowForm] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  const fetchDocuments = useCallback(() => filesService.getDocuments ? filesService.getDocuments() : Promise.resolve([]), []);
  const { data: resp, loading, refresh } = useApi(fetchDocuments, []);
  const documents = resp?.results || resp || [];

  const handleUploadDocument = async (formData) => {
    try {
      const formDataObj = new FormData();
      Object.keys(formData).forEach(key => {
        formDataObj.append(key, formData[key]);
      });
      await filesService.uploadFile(formDataObj);
      toast.success('Document uploaded');
      setShowForm(false);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to upload document');
    }
  };

  return (
    <div className="document-upload">
      <div className="header">
        <h1>Document Upload</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          Upload Document
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            fields={[
              { name: 'documentType', label: 'Document Type', type: 'select', required: true },
              { name: 'description', label: 'Description', type: 'textarea' },
              { name: 'file', label: 'File', type: 'file', required: true }
            ]}
            onSubmit={handleUploadDocument}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      <Table
        data={documents}
        columns={[
          { key: 'type', label: 'Type' },
          { key: 'fileName', label: 'File Name' },
          { key: 'uploadDate', label: 'Upload Date' },
          { key: 'status', label: 'Status', render: (status) => <Badge status={status} /> }
        ]}
        loading={loading}
      />
    </div>
  );
}
