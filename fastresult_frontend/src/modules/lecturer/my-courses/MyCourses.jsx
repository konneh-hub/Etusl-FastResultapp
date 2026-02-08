import React, { useCallback, useState, useMemo } from 'react';
import Table from '../../../../components/Table/Table';
import Badge from '../../../../components/Badge/Badge';
import './MyCourses.css';
import useApi from '../../../../hooks/useApi';
import * as courseService from '../../../../services/courseService';
import { useAuth } from '../../../../hooks/useAuth';

export default function MyCourses() {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [limit] = useState(20);

  const fetchCourses = useCallback(
    () => courseService.getCourses({ page, pageSize: limit, filters: { lecturer: user?.id } }),
    [page, limit, user?.id]
  );
  const { data: coursesResp, loading: isLoading } = useApi(fetchCourses, [page, limit, user?.id]);

  const courses = coursesResp?.results || [];

  return (
    <div className="my-courses">
      <h1>My Courses</h1>

      {isLoading ? (
        <div className="loading">Loading courses...</div>
      ) : courses.length === 0 ? (
        <div className="empty-state">No courses assigned yet</div>
      ) : (
        <Table
          data={courses}
          columns={[
            { key: 'code', label: 'Course Code' },
            { key: 'name', label: 'Course Title' },
            { key: 'semester', label: 'Semester' },
            { key: 'student_count', label: 'Students' },
            { key: 'status', label: 'Status', render: (status) => <Badge status={status} /> }
          ]}
        />
      )}
    </div>
  );
}
