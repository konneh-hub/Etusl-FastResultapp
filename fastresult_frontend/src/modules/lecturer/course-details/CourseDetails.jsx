import React, { useCallback, useParams } from 'react';
import Table from '../../../../components/Table/Table';
import Badge from '../../../../components/Badge/Badge';
import useApi from '../../../../hooks/useApi';
import * as courseService from '../../../../services/courseService';
import './CourseDetails.css';

export default function CourseDetails() {
  const { courseId } = useParams();

  const fetchCourseDetails = useCallback(() => courseService.getCourse(courseId), [courseId]);
  const { data: courseDetails, loading } = useApi(fetchCourseDetails, [courseId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="course-details">
      <h1>Course Details</h1>

      {courseDetails && (
        <>
          <div className="course-info">
            <div className="info-field">
              <label>Course Code:</label>
              <p>{courseDetails.code}</p>
            </div>
            <div className="info-field">
              <label>Course Title:</label>
              <p>{courseDetails.title}</p>
            </div>
            <div className="info-field">
              <label>Credits:</label>
              <p>{courseDetails.credits}</p>
            </div>
            <div className="info-field">
              <label>Enrolled Students:</label>
              <p>{courseDetails.enrolledStudents}</p>
            </div>
          </div>

          <div className="course-sections">
            <h2>Course Sections</h2>
            <Table
              data={courseDetails.sections || []}
              columns={[
                { key: 'title', label: 'Section Title' },
                { key: 'description', label: 'Description' },
                { key: 'status', label: 'Status', render: (status) => <Badge status={status} /> }
              ]}
            />
          </div>
        </>
      )}
    </div>
  );
}
