import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './guards/roleGuard'
import DashboardLayout from '../layouts/DashboardLayout'

// Import dashboard modules (existing structure in src/modules/)
import AdminDashboard from '../modules/admin/dashboard/AdminDashboard'
import AdminUsers from '../modules/admin/users/UsersManagement'
import AdminFaculties from '../modules/admin/faculties/FacultiesManagement'

import DeanDashboard from '../modules/dean/dashboard/DeanDashboard'
import HodDashboard from '../modules/hod/dashboard/HODDashboard'
import ExamOfficerDashboard from '../modules/examOfficer/dashboard/ExamOfficerDashboard'
import LecturerDashboard from '../modules/lecturer/dashboard/LecturerDashboard'
import StudentDashboard from '../modules/student/dashboard/StudentDashboard'

export default function Router() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" />} />
      <Route path="/login" element={<div>Login Page</div>} />
      <Route path="/access-denied" element={<div>Access Denied</div>} />
      
      <Route path="/admin/*" element={
        <ProtectedRoute roles={['university_admin']}>
          <DashboardLayout>
            <Routes>
              <Route index element={<AdminDashboard />} />
              <Route path="users" element={<AdminUsers />} />
              <Route path="faculties" element={<AdminFaculties />} />
            </Routes>
          </DashboardLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/dean/*" element={
        <ProtectedRoute roles={['dean']}>
          <DashboardLayout>
            <Routes>
              <Route index element={<DeanDashboard />} />
            </Routes>
          </DashboardLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/hod/*" element={
        <ProtectedRoute roles={['hod']}>
          <DashboardLayout>
            <Routes>
              <Route index element={<HodDashboard />} />
            </Routes>
          </DashboardLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/exam/*" element={
        <ProtectedRoute roles={['exam_officer']}>
          <DashboardLayout>
            <Routes>
              <Route index element={<ExamOfficerDashboard />} />
            </Routes>
          </DashboardLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/lecturer/*" element={
        <ProtectedRoute roles={['lecturer']}>
          <DashboardLayout>
            <Routes>
              <Route index element={<LecturerDashboard />} />
            </Routes>
          </DashboardLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/student/*" element={
        <ProtectedRoute roles={['student']}>
          <DashboardLayout>
            <Routes>
              <Route index element={<StudentDashboard />} />
            </Routes>
          </DashboardLayout>
        </ProtectedRoute>
      } />
    </Routes>
  )
}
