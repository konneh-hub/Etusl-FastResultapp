import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as examsService from '../../../../services/examsService';
import toast from 'react-hot-toast';
import './ExamSetup.css';

export default function ExamSetup() {
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
    <div className="exam-setup">
      <div className="header">
        <h1>Exam Setup</h1>
        <button className="btn btn-primary" onClick={() => { setEditingExam(null); setShowForm(true); }}>
          Create Exam
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <Form
            fields={[
              { name: 'title', label: 'Exam Title', type: 'text', required: true },
              { name: 'code', label: 'Exam Code', type: 'text', required: true },
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
          { key: 'actions', label: 'Actions', render: (_, row) => (
            <div>
              <button onClick={() => { setEditingExam(row); setShowForm(true); }}>Edit</button>
            </div>
          )}
        ]}
        loading={loading}
      />
    </div>
  );
}
