import React, { useState, useCallback } from 'react';
import Form from '../../../../components/Form/Form';
import useApi from '../../../../hooks/useApi';
import * as examsService from '../../../../services/examsService';
import toast from 'react-hot-toast';
import './TimetableBuilder.css';

export default function TimetableBuilder() {
  const [isEditing, setIsEditing] = useState(false);
  const [serverErrors, setServerErrors] = useState({});

  const fetchTimetable = useCallback(() => examsService.getTimetables(), []);
  const { data: resp, loading, refresh } = useApi(fetchTimetable, []);
  const timetable = resp?.results?.[0] || resp || null;

  const handleSaveTimetable = async (formData) => {
    try {
      if (timetable?.id) {
        await examsService.updateTimetable(timetable.id, formData);
        toast.success('Timetable updated');
      } else {
        await examsService.createTimetable(formData);
        toast.success('Timetable created');
      }
      setIsEditing(false);
      setServerErrors({});
      await refresh();
    } catch (error) {
      setServerErrors(error.response?.data || {});
      toast.error('Failed to save timetable');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="timetable-builder">
      <div className="header">
        <h1>Timetable Builder</h1>
        {!isEditing && (
          <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
            Edit Timetable
          </button>
        )}
      </div>

      {isEditing ? (
        <Form
          fields={[
            { name: 'examPeriod', label: 'Exam Period', type: 'select', required: true },
            { name: 'startDate', label: 'Start Date', type: 'date', required: true },
            { name: 'endDate', label: 'End Date', type: 'date', required: true },
            { name: 'coursesPerDay', label: 'Courses Per Day', type: 'number', required: true }
          ]}
          initialData={timetable}
          onSubmit={handleSaveTimetable}
          onCancel={() => setIsEditing(false)}
        />
      ) : (
        <div className="timetable-view">
          {timetable && <p>Timetable ready for use</p>}
        </div>
      )}
    </div>
  );
}
