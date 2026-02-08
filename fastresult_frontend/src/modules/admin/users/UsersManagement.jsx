import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import adminService from '../../../services/admin.service'
import FormModal from '../../../components/Form/FormModal'
import FormField from '../../../components/Form/FormField'
import SubmitButton from '../../../components/Form/SubmitButton'
import ConfirmDialog from '../../../components/Dialog/ConfirmDialog'

/**
 * Users Management Page
 * CRUD operations for system users
 */
export default function UsersManagement() {
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    role: 'lecturer',
    is_active: true
  })
  const [isSaving, setSaving] = useState(false)

  // Load users on mount
  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setIsLoading(true)
      const data = await adminService.listUsers()
      setUsers(data.results || data)
    } catch (error) {
      toast.error('Failed to load users: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  // Filter users by search term
  const filteredUsers = users.filter(u =>
    u.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Open modal for creating user
  const handleCreate = () => {
    setSelectedUser(null)
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      role: 'lecturer',
      is_active: true
    })
    setIsModalOpen(true)
  }

  // Open modal for editing user
  const handleEdit = (user) => {
    setSelectedUser(user)
    setFormData({
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      role: user.role,
      is_active: user.is_active
    })
    setIsModalOpen(true)
  }

  // Save user (create or update)
  const handleSave = async (e) => {
    e.preventDefault()
    try {
      setSaving(true)

      if (selectedUser) {
        // Update existing user
        await adminService.updateUser(selectedUser.id, formData)
        setUsers(users.map(u => u.id === selectedUser.id ? { ...u, ...formData } : u))
        toast.success('User updated successfully')
      } else {
        // Create new user
        const newUser = await adminService.createUser(formData)
        setUsers([...users, newUser])
        toast.success('User created successfully')
      }

      setIsModalOpen(false)
    } catch (error) {
      toast.error('Failed to save user: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  // Delete user
  const handleDelete = async () => {
    try {
      setSaving(true)
      await adminService.deleteUser(selectedUser.id)
      setUsers(users.filter(u => u.id !== selectedUser.id))
      setIsDeleteOpen(false)
      toast.success('User deleted successfully')
    } catch (error) {
      toast.error('Failed to delete user: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Users Management</h1>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus size={18} /> New User
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-3 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search by name or email..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading users...</div>
        ) : filteredUsers.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No users found</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-100 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold">Name</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Email</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Role</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map(user => (
                <tr key={user.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-3">{user.first_name} {user.last_name}</td>
                  <td className="px-6 py-3 text-sm text-gray-600">{user.email}</td>
                  <td className="px-6 py-3">
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-3 flex gap-2">
                    <button
                      onClick={() => handleEdit(user)}
                      className="p-2 hover:bg-blue-100 rounded text-blue-600 transition"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button
                      onClick={() => {
                        setSelectedUser(user)
                        setIsDeleteOpen(true)
                      }}
                      className="p-2 hover:bg-red-100 rounded text-red-600 transition"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Create/Edit Modal */}
      <FormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedUser ? 'Edit User' : 'Create New User'}
        maxWidth="max-w-md"
      >
        <form onSubmit={handleSave} className="space-y-4">
          <FormField
            label="First Name"
            required
            value={formData.first_name}
            onChange={e => setFormData({...formData, first_name: e.target.value})}
            placeholder="John"
          />
          <FormField
            label="Last Name"
            required
            value={formData.last_name}
            onChange={e => setFormData({...formData, last_name: e.target.value})}
            placeholder="Doe"
          />
          <FormField
            label="Email"
            type="email"
            required
            value={formData.email}
            onChange={e => setFormData({...formData, email: e.target.value})}
            placeholder="john@example.com"
          />
          <FormField
            label="Role"
            as="select"
            required
            value={formData.role}
            onChange={e => setFormData({...formData, role: e.target.value})}
            options={[
              { value: 'lecturer', label: 'Lecturer' },
              { value: 'hod', label: 'Head of Department' },
              { value: 'dean', label: 'Dean' },
              { value: 'exam_officer', label: 'Exam Officer' },
              { value: 'university_admin', label: 'University Admin' }
            ]}
          />
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="active"
              checked={formData.is_active}
              onChange={e => setFormData({...formData, is_active: e.target.checked})}
              className="rounded"
            />
            <label htmlFor="active" className="text-sm">Active</label>
          </div>

          <div className="flex gap-2 pt-4">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <SubmitButton
              isLoading={isSaving}
              className="flex-1"
            >
              {selectedUser ? 'Update User' : 'Create User'}
            </SubmitButton>
          </div>
        </form>
      </FormModal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={isDeleteOpen}
        onConfirm={handleDelete}
        onCancel={() => setIsDeleteOpen(false)}
        title="Delete User"
        message={`Are you sure you want to delete ${selectedUser?.first_name} ${selectedUser?.last_name}?`}
        confirmText="Delete"
        isLoading={isSaving}
      />
    </div>
  )
}
