import React, { useState, useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import Badge from '../../../../components/Badge/Badge';
import useApi from '../../../../hooks/useApi';
import * as resultService from '../../../../services/resultService';
import toast from 'react-hot-toast';
import './ResultsControl.css';

export default function ResultsControl() {
  const [statusFilter, setStatusFilter] = useState('all');

  const fetchResults = useCallback(() => resultService.getResults({ status: statusFilter }), [statusFilter]);
  const { data: resp, loading, refresh } = useApi(fetchResults, [statusFilter]);
  const results = resp?.results || resp || [];

  const handleApprove = async (resultId) => {
    try {
      await resultService.updateResult(resultId, { status: 'approved' });
      toast.success('Result approved');
      await refresh();
    } catch (error) {
      toast.error('Failed to approve result');
    }
  };

  const handleReject = async (resultId) => {
    try {
      await resultService.updateResult(resultId, { status: 'rejected' });
      toast.success('Result rejected');
      await refresh();
    } catch (error) {
      toast.error('Failed to reject result');
    }
  };

  return (
    <div className="results-control">
      <h1>Results Control</h1>

      <div className="filters">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">All Results</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      <Table
        data={results}
        columns={[
          { key: 'semester', label: 'Semester' },
          { key: 'lecturer', label: 'Lecturer' },
          { key: 'course', label: 'Course' },
          { key: 'studentsCount', label: 'Students' },
          { key: 'status', label: 'Status', render: (status) => <Badge status={status} /> },
          { key: 'actions', label: 'Actions', render: (_, row) => (
            <div className="action-buttons">
              <button onClick={() => handleApprove(row.id)}>Approve</button>
              <button onClick={() => handleReject(row.id)}>Reject</button>
            </div>
          )}
        ]}
        loading={loading}
      />
    </div>
  );
}
