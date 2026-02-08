import React, { useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import Badge from '../../../../components/Badge/Badge';
import useApi from '../../../../hooks/useApi';
import * as academicService from '../../../../services/academicService';
import './FacultyOversight.css';

export default function FacultyOversight() {
  const fetchFaculties = useCallback(() => academicService.getFaculties(), []);
  const { data: resp, loading } = useApi(fetchFaculties, []);
  const faculties = resp?.results || resp || [];

  return (
    <div className="faculty-oversight">
      <h1>Faculty Oversight</h1>
      
      <Table
        data={faculties}
        columns={[
          { key: 'name', label: 'Faculty Name' },
          { key: 'hod', label: 'Head of Department' },
          { key: 'departmentCount', label: 'Departments' },
          { key: 'studentCount', label: 'Students' },
          { key: 'status', label: 'Status', render: (status) => <Badge status={status} /> }
        ]}
        loading={loading}
        onRowClick={(row) => console.log('Viewing faculty:', row)}
      />
    </div>
  );
}
