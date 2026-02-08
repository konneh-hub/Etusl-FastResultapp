import React, { useState, useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as academicService from '../../../../services/academicService';
import './AcademicLists.css';

export default function AcademicLists() {
  const [listType, setListType] = useState('faculties');

  const fetchData = useCallback(() => {
    switch (listType) {
      case 'faculties': return academicService.getFaculties();
      case 'departments': return academicService.getDepartments();
      case 'programs': return academicService.getPrograms();
      default: return academicService.getCourses ? academicService.getCourses() : Promise.resolve([]);
    }
  }, [listType]);
  const { data: resp, loading } = useApi(fetchData, [listType]);
  const academicData = resp?.results || resp || [];

  return (
    <div className="academic-lists">
      <h1>Academic Lists</h1>

      <div className="list-selector">
        <select value={listType} onChange={(e) => setListType(e.target.value)}>
          <option value="faculties">Faculties</option>
          <option value="departments">Departments</option>
          <option value="programs">Programs</option>
          <option value="courses">Courses</option>
        </select>
      </div>

      <Table
        data={academicData}
        columns={[
          { key: 'code', label: 'Code' },
          { key: 'name', label: 'Name' },
          { key: 'head', label: 'Head' },
          { key: 'status', label: 'Status' }
        ]}
        loading={loading}
      />
    </div>
  );
}
