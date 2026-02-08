import React, { useCallback, useState } from 'react';
import Table from '../../../../components/Table/Table';
import Badge from '../../../../components/Badge/Badge';
import './Courses.css';
import useApi from '../../../../hooks/useApi';
import * as courseService from '../../../../services/courseService';
import { useAuth } from '../../../../hooks/useAuth';

export default function Courses() {
  const { user } = useAuth();
  const [semesterFilter, setSemesterFilter] = useState('current');

  const fetchCourses = useCallback(
    () => courseService.getCourses({ filters: { student: user?.id, semester: semesterFilter } }),
    [user?.id, semesterFilter]
  );
  const { data: coursesResp, loading: isLoading } = useApi(fetchCourses, [user?.id, semesterFilter]);

  const courses = coursesResp?.results || coursesResp || [];

  return (
    <div className="student-courses">
      <h1>My Courses</h1>

      <div className="filters">
        <select value={semesterFilter} onChange={(e) => setSemesterFilter(e.target.value)}>
          <option value="current">Current Semester</option>
          <option value="previous">Previous Semester</option>
          <option value="">All Semesters</option>
        </select>
      </div>

      {isLoading ? (
        <div className="loading">Loading courses...</div>
      ) : courses.length === 0 ? (
        <div className="empty-state">No courses found</div>
      ) : (
        <Table
          data={courses}
          columns={[
            { key: 'code', label: 'Course Code' },
            { key: 'name', label: 'Course Title' },
            { key: 'credits', label: 'Credits' },
            { key: 'lecturer_name', label: 'Lecturer' },
            { key: 'status', label: 'Status', render: (status) => <Badge status={status} /> }
          ]}
        />
      )}
    </div>
  );
}
