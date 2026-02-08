import React, { useState, useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import Badge from '../../../../components/Badge/Badge';
import useApi from '../../../../hooks/useApi';
import * as courseService from '../../../../services/courseService';
import './SubmissionStatus.css';

export default function SubmissionStatus() {
  const [statusFilter, setStatusFilter] = useState('all');

  const fetchSubmissions = useCallback(() => courseService.getCourses({ status: statusFilter }), [statusFilter]);
  const { data: resp, loading } = useApi(fetchSubmissions, [statusFilter]);
  const submissions = resp?.results || resp || [];

  return (
    <div className="submission-status">
      <h1>Submission Status</h1>

      <div className="filters">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">All Submissions</option>
          <option value="pending">Pending</option>
          <option value="submitted">Submitted</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      <Table
        data={submissions}
        columns={[
          { key: 'course', label: 'Course' },
          { key: 'semester', label: 'Semester' },
          { key: 'submissionDate', label: 'Submission Date' },
          { key: 'status', label: 'Status', render: (status) => <Badge status={status} /> },
          { key: 'approvalDate', label: 'Approval Date' }
        ]}
        loading={loading}
      />
    </div>
  );
}
