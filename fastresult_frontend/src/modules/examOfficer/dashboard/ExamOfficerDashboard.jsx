import { useState, useEffect } from 'react'
import StatsCard from '../../../components/cards/StatsCard'
import DataTable from '../../../components/tables/DataTable'

export default function ExamOfficerDashboard() {
  const [stats, setStats] = useState({
    exams: 0,
    applicants: 0,
    submitted: 0,
    pending: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setStats({
        exams: 24,
        applicants: 450,
        submitted: 420,
        pending: 30
      })
    } catch (error) {
      console.error('Failed to fetch dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Exam Officer Dashboard</h1>
        <p className="text-gray-600">Manage exams and results verification</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard label="Active Exams" value={stats.exams} icon="📝" />
        <StatsCard label="Applicants" value={stats.applicants} icon="📋" />
        <StatsCard label="Submitted" value={stats.submitted} icon="✅" />
        <StatsCard label="Pending" value={stats.pending} icon="⏳" />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button className="bg-blue-500 text-white p-4 rounded-lg hover:bg-blue-600">
          📋 Exam Schedule
        </button>
        <button className="bg-green-500 text-white p-4 rounded-lg hover:bg-green-600">
          📊 Verify Results
        </button>
        <button className="bg-purple-500 text-white p-4 rounded-lg hover:bg-purple-600">
          📈 Statistics
        </button>
      </div>
    </div>
  )
}
