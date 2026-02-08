import React, { useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as courseService from '../../../../services/courseService';
import './Registration.css';

export default function Registration() {
  const fetchRegistrations = useCallback(() => courseService.getCourses(), []);
  const { data: resp, loading } = useApi(fetchRegistrations, []);
  const registrations = resp?.results || resp || [];

  return (
    <div className="registration">
      <h1>Course Registration History</h1>

      <Table
        data={registrations}
        columns={[
          { key: 'course', label: 'Course' },
          { key: 'semester', label: 'Semester' },
          { key: 'year', label: 'Year' },
          { key: 'registrationDate', label: 'Registration Date' },
          { key: 'status', label: 'Status' }
        ]}
        loading={loading}
      />
    </div>
  );
}
