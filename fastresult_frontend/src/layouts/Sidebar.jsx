import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Sidebar(){
  const { user } = useAuth()

  const menuByRole = {
    'university_admin': [
      {to: '/admin/dashboard', label: 'Dashboard'},
      {to: '/admin/users', label: 'Users'},
      {to: '/admin/faculties', label: 'Faculties'},
      {to: '/admin/departments', label: 'Departments'},
      {to: '/admin/programs', label: 'Programs'},
      {to: '/admin/courses', label: 'Courses'},
      {to: '/admin/academic-year', label: 'Academic Year'},
      {to: '/admin/grading-scale', label: 'Grading Scale'},
      {to: '/admin/result-control', label: 'Result Control'},
      {to: '/admin/reports', label: 'Reports'},
    ],
    'dean': [
      {to: '/dean/dashboard', label: 'Faculty Dashboard'},
      {to: '/dean/departments', label: 'Departments'},
      {to: '/dean/reports', label: 'Reports'},
    ],
    'hod': [
      {to: '/hod/dashboard', label: 'Department Overview'},
      {to: '/hod/assignments', label: 'Assignments'},
      {to: '/hod/results-review', label: 'Results Review'},
    ],
    'exam_officer': [
      {to: '/exam/verification', label: 'Verification Queue'},
      {to: '/exam/scheduling', label: 'Scheduling'},
    ],
    'lecturer': [
      {to: '/lecturer/my-courses', label: 'My Courses'},
      {to: '/lecturer/result-entry', label: 'Result Entry'},
    ],
    'student': [
      {to: '/student/dashboard', label: 'Dashboard'},
      {to: '/student/transcript', label: 'Transcript'},
    ]
  }

  const items = user && menuByRole[user.role] ? menuByRole[user.role] : []

  return (
    <aside className="sidebar">
      <div className="brand">SRMS</div>
      <nav>
        {items.map(i => (
          <Link key={i.to} to={i.to} className="menu-item">{i.label}</Link>
        ))}
      </nav>
    </aside>
  )
}
