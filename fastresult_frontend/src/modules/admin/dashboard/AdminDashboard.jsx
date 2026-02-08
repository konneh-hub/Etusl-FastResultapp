import { useState, useEffect } from 'react'
import StatsCard from '../../../components/cards/StatsCard'
import DataTable from '../../../components/tables/DataTable'

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    universities: 0,
    systemHealth: 0
  })
  const [recentActivities, setRecentActivities] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setStats({
        totalUsers: 2542,
        activeUsers: 1856,
        universities: 5,
        systemHealth: 98
      })
      setRecentActivities([
        {
          id: 1,
          user: 'John Doe',
          action: 'User Registered',
          timestamp: '5 mins ago'
        },
        {
          id: 2,
          user: 'System',
          action: 'Database Backup',
          timestamp: '1 hour ago'
        }
      ])
    } catch (error) {
      console.error('Failed to fetch dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { header: 'User', accessor: 'user' },
    { header: 'Action', accessor: 'action' },
    { header: 'Time', accessor: 'timestamp' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600">System overview and management</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard label="Total Users" value={stats.totalUsers} icon="👥" />
        <StatsCard label="Active" value={stats.activeUsers} icon="🟢" />
        <StatsCard label="Universities" value={stats.universities} icon="🏫" />
        <StatsCard label="System Health" value={`${stats.systemHealth}%`} icon="💚" />
      </div>

      {/* Recent Activities */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activities</h2>
        <DataTable 
          columns={columns}
          data={recentActivities}
          loading={loading}
        />
      </div>

      {/* Management Sections */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg cursor-pointer">
          <h3 className="text-lg font-semibold mb-2">👥 User Management</h3>
          <p className="text-gray-600 text-sm">Create and manage user accounts</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg cursor-pointer">
          <h3 className="text-lg font-semibold mb-2">🏫 Universities</h3>
          <p className="text-gray-600 text-sm">Manage universities and campuses</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg cursor-pointer">
          <h3 className="text-lg font-semibold mb-2">📊 Reports</h3>
          <p className="text-gray-600 text-sm">View system reports and analytics</p>
        </div>
      </div>

      {/* Admin Actions */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <button className="bg-blue-500 text-white p-4 rounded-lg hover:bg-blue-600">
          ➕ Add User
        </button>
        <button className="bg-green-500 text-white p-4 rounded-lg hover:bg-green-600">
          🏫 Add University
        </button>
        <button className="bg-purple-500 text-white p-4 rounded-lg hover:bg-purple-600">
          📋 System Logs
        </button>
        <button className="bg-orange-500 text-white p-4 rounded-lg hover:bg-orange-600">
          ⚙️ Settings
        </button>
      </div>
    </div>
  )
}
