import React, { useCallback, useState } from 'react';
import Table from '../../../../components/Table/Table';
import './EnrolledStudents.css';
import useApi from '../../../../hooks/useApi';
import * as courseService from '../../../../services/courseService';
import { useAuth } from '../../../../hooks/useAuth';

export default function EnrolledStudents() {
  const { user } = useAuth();
  const [courseFilter, setCourseFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [limit] = useState(50);

  const fetchCourses = useCallback(() => courseService.getCourses({ filters: { lecturer: user?.id } }), [user?.id]);
  const { data: coursesResp } = useApi(fetchCourses, [user?.id]);

  const fetchStudents = useCallback(() => {
    if (!courseFilter || courseFilter === 'all') {
      return Promise.resolve({ results: [] });
    }
    return courseService.getEnrolledStudents(courseFilter, { page, pageSize: limit });
  }, [courseFilter, page, limit]);
  const { data: studentsResp, loading: isLoading } = useApi(fetchStudents, [courseFilter, page, limit]);

  const students = studentsResp?.results || [];
  const courses = coursesResp?.results || [];

  return (
    <div className="enrolled-students">
      <h1>Enrolled Students</h1>

      <div className="filters">
        <select value={courseFilter} onChange={(e) => setCourseFilter(e.target.value)}>
          <option value="all">All Courses</option>
          {courses.map(course => (
            <option key={course.id} value={course.id}>{course.name}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="loading">Loading students...</div>
      ) : students.length === 0 ? (
        <div className="empty-state">No students found</div>
      ) : (
        <Table
          data={students}
          columns={[
            { key: 'student_id', label: 'Student ID' },
            { key: 'first_name', label: 'Name' },
            { key: 'email', label: 'Email' },
            { key: 'enrollment_date', label: 'Enrollment Date' },
            { key: 'status', label: 'Status' }
          ]}
        />
      )}
    </div>
  );
}
