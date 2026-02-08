import React, { useState, useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import Badge from '../../../../components/Badge/Badge';
import useApi from '../../../../hooks/useApi';
import * as resultService from '../../../../services/resultService';
import toast from 'react-hot-toast';
import './ResultVerification.css';

export default function ResultVerification() {
  const [statusFilter, setStatusFilter] = useState('pending');

  const fetchResults = useCallback(() => resultService.getResults({ status: statusFilter }), [statusFilter]);
  const { data: resp, loading, refresh } = useApi(fetchResults, [statusFilter]);
  const results = resp?.results || resp || [];

  const handleVerify = async (resultId) => {
    try {
      await resultService.verifyResult(resultId);
      toast.success('Result verified');
      await refresh();
    } catch (error) {
      toast.error('Failed to verify result');
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
    <div className="result-verification">
      <h1>Result Verification</h1>

      <div className="filters">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="pending">Pending</option>
          <option value="verified">Verified</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      <Table
        data={results}
        columns={[
          { key: 'course', label: 'Course' },
          { key: 'lecturer', label: 'Lecturer' },
          { key: 'studentsCount', label: 'Students' },
          { key: 'status', label: 'Status', render: (status) => <Badge status={status} /> },
          { key: 'actions', label: 'Actions', render: (_, row) => (
            <div className="action-buttons">
              <button onClick={() => handleVerify(row.id)}>Verify</button>
              <button onClick={() => handleReject(row.id)}>Reject</button>
            </div>
          )}
        ]}
        loading={loading}
      />
    </div>
  );
}
