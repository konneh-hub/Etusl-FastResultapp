import React, { useState, useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as academicService from '../../../../services/academicService';
import './AcademicLists.css';

export default function AcademicLists() {
  const [listType, setListType] = useState('programs');

  const fetchData = useCallback(() => {
    switch (listType) {
      case 'programs': return academicService.getPrograms();
      case 'courses': return academicService.getCourses ? academicService.getCourses() : Promise.resolve([]);
      default: return Promise.resolve([]);
    }
  }, [listType]);
  const { data: resp, loading } = useApi(fetchData, [listType]);
  const academicData = resp?.results || resp || [];

  return (
    <div className="hod-academic-lists">
      <h1>Academic Lists</h1>

      <div className="list-selector">
        <select value={listType} onChange={(e) => setListType(e.target.value)}>
          <option value="programs">Programs</option>
          <option value="courses">Courses</option>
          <option value="levels">Levels</option>
        </select>
      </div>

      <Table
        data={academicData}
        columns={[
          { key: 'code', label: 'Code' },
          { key: 'name', label: 'Name' },
          { key: 'description', label: 'Description' },
          { key: 'status', label: 'Status' }
        ]}
        loading={loading}
      />
    </div>
  );
}
