import { useState, useCallback, useMemo } from 'react'
import StatsCard from '../../../components/cards/StatsCard'
import useApi from '../../../hooks/useApi'
import * as dashboardService from '../../../services/dashboardService'
import { useAuth } from '../../../hooks/useAuth'
import authService from '../../../services/auth.service'

export default function DeanDashboard() {
  const { user } = useAuth()
  const currentUser = authService.getCurrentUser()
  const scope = useMemo(() => ({
    role: 'dean',
    facultyId: currentUser?.faculty || currentUser?.faculty_id || currentUser?.facultyId
  }), [currentUser])

  const fetchTotals = useCallback(() => dashboardService.getTotals(scope), [scope])
  const fetchStats = useCallback(() => dashboardService.getStatistics(scope), [scope])
  const fetchKpis = useCallback(() => dashboardService.getKpis(scope), [scope])

  const { data: totals, loading: loadingTotals } = useApi(fetchTotals, [scope])
  const { data: statistics } = useApi(fetchStats, [scope])
  const { data: kpis } = useApi(fetchKpis, [scope])

  const stats = {
    faculties: totals?.faculties_count || 0,
    departments: totals?.departments_count || 0,
    staff: totals?.lecturers_count || 0,
    approvalsPending: statistics?.pending_approvals || 0
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dean Dashboard</h1>
        <p className="text-gray-600">Faculty-wide oversight and approvals</p>
      </div>

      {loadingTotals ? (
        <div className="loading">Loading dashboard...</div>
      ) : (
        <>
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatsCard label="Faculties" value={stats.faculties} icon="🏛️" />
            <StatsCard label="Departments" value={stats.departments} icon="🏢" />
            <StatsCard label="Staff" value={stats.staff} icon="👨‍💼" />
            <StatsCard label="Pending Approvals" value={stats.approvalsPending} icon="⏳" />
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="bg-blue-500 text-white p-4 rounded-lg hover:bg-blue-600">
              ✅ Approvals Review
            </button>
            <button className="bg-green-500 text-white p-4 rounded-lg hover:bg-green-600">
              📊 Faculty Reports
            </button>
            <button className="bg-purple-500 text-white p-4 rounded-lg hover:bg-purple-600">
              👥 Staff Management
            </button>
          </div>
        </>
      )}
    </div>
  )
}
