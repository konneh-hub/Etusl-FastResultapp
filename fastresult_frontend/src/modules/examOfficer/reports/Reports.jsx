import React, { useState, useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as reportService from '../../../../services/reportService';
import toast from 'react-hot-toast';
import './Reports.css';

export default function ExamOfficerReports() {
  const [reportType, setReportType] = useState('all');

  const fetchReports = useCallback(() => reportService.getReports({ type: reportType }), [reportType]);
  const { data: resp, loading } = useApi(fetchReports, [reportType]);
  const reports = resp?.results || resp || [];

  const handleDownload = async (report) => {
    try {
      const blob = await reportService.downloadReport(report.id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${report.name}.pdf`;
      link.click();
      toast.success('Report downloaded');
    } catch (error) {
      toast.error('Failed to download report');
    }
  };

  return (
    <div className="exam-officer-reports">
      <h1>Reports</h1>

      <div className="filters">
        <select value={reportType} onChange={(e) => setReportType(e.target.value)}>
          <option value="all">All Reports</option>
          <option value="exam">Exam Reports</option>
          <option value="verification">Verification Reports</option>
          <option value="analytics">Analytics</option>
        </select>
      </div>

      <Table
        data={reports}
        columns={[
          { key: 'name', label: 'Report Name' },
          { key: 'type', label: 'Type' },
          { key: 'date', label: 'Generated Date' },
          { key: 'actions', label: 'Actions', render: (_, row) => (
            <button onClick={() => handleDownload(row)}>Download</button>
          )}
        ]}
        loading={loading}
      />
    </div>
  );
}
