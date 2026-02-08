import React, { useCallback, useState } from 'react';
import Table from '../../../../components/Table/Table';
import './SemesterResults.css';
import useApi from '../../../../hooks/useApi';
import * as resultService from '../../../../services/resultService';
import { useAuth } from '../../../../hooks/useAuth';

export default function SemesterResults() {
  const { user } = useAuth();
  const [semesterFilter, setSemesterFilter] = useState('current');

  const fetchResults = useCallback(
    () => resultService.getStudentResults(user?.id, { filters: { semester: semesterFilter } }),
    [user?.id, semesterFilter]
  );
  const { data: resultsResp, loading: isLoading } = useApi(fetchResults, [user?.id, semesterFilter]);

  const results = resultsResp?.results || resultsResp || [];

  return (
    <div className="semester-results">
      <h1>Semester Results</h1>

      <div className="filters">
        <select value={semesterFilter} onChange={(e) => setSemesterFilter(e.target.value)}>
          <option value="current">Current Semester</option>
          <option value="previous">Previous Semester</option>
          <option value="">All Semesters</option>
        </select>
      </div>

      {isLoading ? (
        <div className="loading">Loading results...</div>
      ) : results.length === 0 ? (
        <div className="empty-state">No results found for this semester</div>
      ) : (
        <Table
          data={results}
          columns={[
            { key: 'course_code', label: 'Course Code' },
            { key: 'course_title', label: 'Course Title' },
            { key: 'credits', label: 'Credits' },
            { key: 'score', label: 'Score' },
            { key: 'grade', label: 'Grade' },
            { key: 'gpa', label: 'GPA' }
          ]}
        />
      )}
    </div>
  );
}
