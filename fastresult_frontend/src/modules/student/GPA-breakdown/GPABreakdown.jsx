import React, { useCallback } from 'react';
import Chart from 'chart.js/auto';
import useApi from '../../../../hooks/useApi';
import * as resultService from '../../../../services/resultService';
import './GPABreakdown.css';

export default function GPABreakdown() {
  const chartRef = React.useRef(null);

  const fetchGPAData = useCallback(() => resultService.getStudentResults(), []);
  const { data: gpaData, loading } = useApi(fetchGPAData, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="gpa-breakdown">
      <h1>GPA Breakdown</h1>

      {gpaData && (
        <>
          <div className="gpa-summary">
            <div className="summary-card">
              <label>Current GPA:</label>
              <p className="large-number">{gpaData.currentGpa}</p>
            </div>
            <div className="summary-card">
              <label>CGPA:</label>
              <p className="large-number">{gpaData.cgpa}</p>
            </div>
            <div className="summary-card">
              <label>Total Credits:</label>
              <p className="large-number">{gpaData.totalCredits}</p>
            </div>
          </div>

          <div className="chart-container">
            <canvas ref={chartRef}></canvas>
          </div>

          <div className="gpa-details">
            <h2>Semester Breakdown</h2>
            {/* TODO: Add semester details table */}
          </div>
        </>
      )}
    </div>
  );
}
