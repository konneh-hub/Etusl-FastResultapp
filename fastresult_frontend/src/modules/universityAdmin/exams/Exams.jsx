import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as examsService from '../../../../services/examsService';
import toast from 'react-hot-toast';
import './Exams.css';

export default function Exams() {
  const [showForm, setShowForm] = useState(false);
  const [editingExam, setEditingExam] = useState(null);
  const [serverErrors, setServerErrors] = useState({});

  const fetchExams = useCallback(() => examsService.getExams(), []);
  const { data: resp, loading, refresh } = useApi(fetchExams, []);
  const exams = resp?.results || resp || [];

  const handleSaveExam = async (formData) => {
    try {
      if (editingExam?.id) {
        await examsService.updateExam(editingExam.id, formData);
        toast.success('Exam updated');
      } else {
        await examsService.createExam(formData);
        toast.success('Exam created');
      }
      setShowForm(false);
      setEditingExam(null);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to save exam');
    }
  };

  return (
    <div className="exams">
      <div className="header">
        <h1>Exams Management</h1>
        <button className="btn btn-primary" onClick={() => { setEditingExam(null); setShowForm(true); }}>
          Create Exam
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            fields={[
              { name: 'code', label: 'Exam Code', type: 'text', required: true },
              { name: 'title', label: 'Title', type: 'text', required: true },
              { name: 'startDate', label: 'Start Date', type: 'date', required: true },
              { name: 'endDate', label: 'End Date', type: 'date', required: true },
              { name: 'period', label: 'Period', type: 'select', required: true }
            ]}
            initialData={editingExam}
            onSubmit={handleSaveExam}
            onCancel={() => { setShowForm(false); setEditingExam(null); }}
          />
        </div>
      )}

      <Table
        data={exams}
        columns={[
          { key: 'code', label: 'Code' },
          { key: 'title', label: 'Title' },
          { key: 'startDate', label: 'Start Date' },
          { key: 'endDate', label: 'End Date' },
          { key: 'period', label: 'Period' }
        ]}
        loading={loading}
      />
    </div>
  );
}
