import React from 'react'

export default function Sidebar() {
  return (
    <div>
      <div className="logo">University Admin</div>
      <ul>
        <li className="active">Dashboard</li>
        <li>Students</li>
        <li>Exams</li>
        <li>Lecturers</li>
        <li>Reports</li>
        <li>Settings</li>
      </ul>
    </div>
  )
}
