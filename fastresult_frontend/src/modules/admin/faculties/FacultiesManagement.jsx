import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import adminService from '../../../services/admin.service'
import FormModal from '../../../components/Form/FormModal'
import FormField from '../../../components/Form/FormField'
import SubmitButton from '../../../components/Form/SubmitButton'
import ConfirmDialog from '../../../components/Dialog/ConfirmDialog'

/**
 * Faculties Management Page
 * CRUD operations for university faculties
 */
export default function FacultiesManagement() {
  const [faculties, setFaculties] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [selectedFaculty, setSelectedFaculty] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: ''
  })
  const [isSaving, setSaving] = useState(false)

  useEffect(() => {
    fetchFaculties()
  }, [])

  const fetchFaculties = async () => {
    try {
      setIsLoading(true)
      const data = await adminService.listFaculties()
      setFaculties(data.results || data)
    } catch (error) {
      toast.error('Failed to load faculties: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredFaculties = faculties.filter(f =>
    f.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    f.code.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleCreate = () => {
    setSelectedFaculty(null)
    setFormData({ name: '', code: '', description: '' })
    setIsModalOpen(true)
  }

  const handleEdit = (faculty) => {
    setSelectedFaculty(faculty)
    setFormData({
      name: faculty.name,
      code: faculty.code,
      description: faculty.description || ''
    })
    setIsModalOpen(true)
  }

  const handleSave = async (e) => {
    e.preventDefault()
    try {
      setSaving(true)

      if (selectedFaculty) {
        await adminService.updateFaculty(selectedFaculty.id, formData)
        setFaculties(faculties.map(f => f.id === selectedFaculty.id ? { ...f, ...formData } : f))
        toast.success('Faculty updated successfully')
      } else {
        const newFaculty = await adminService.createFaculty(formData)
        setFaculties([...faculties, newFaculty])
        toast.success('Faculty created successfully')
      }

      setIsModalOpen(false)
    } catch (error) {
      toast.error('Failed to save faculty: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    try {
      setSaving(true)
      await adminService.deleteFaculty(selectedFaculty.id)
      setFaculties(faculties.filter(f => f.id !== selectedFaculty.id))
      setIsDeleteOpen(false)
      toast.success('Faculty deleted successfully')
    } catch (error) {
      toast.error('Failed to delete faculty: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Faculties Management</h1>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus size={18} /> New Faculty
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-3 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search by name or code..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading faculties...</div>
        ) : filteredFaculties.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No faculties found</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-100 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold">Name</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Code</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Description</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredFaculties.map(faculty => (
                <tr key={faculty.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-3 font-medium">{faculty.name}</td>
                  <td className="px-6 py-3 text-sm text-gray-600">{faculty.code}</td>
                  <td className="px-6 py-3 text-sm text-gray-600 truncate">{faculty.description}</td>
                  <td className="px-6 py-3 flex gap-2">
                    <button
                      onClick={() => handleEdit(faculty)}
                      className="p-2 hover:bg-blue-100 rounded text-blue-600 transition"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button
                      onClick={() => {
                        setSelectedFaculty(faculty)
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

      <FormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedFaculty ? 'Edit Faculty' : 'Create New Faculty'}
        maxWidth="max-w-md"
      >
        <form onSubmit={handleSave} className="space-y-4">
          <FormField
            label="Faculty Name"
            required
            value={formData.name}
            onChange={e => setFormData({...formData, name: e.target.value})}
            placeholder="Faculty of Science"
          />
          <FormField
            label="Code"
            required
            value={formData.code}
            onChange={e => setFormData({...formData, code: e.target.value})}
            placeholder="SCI"
          />
          <FormField
            label="Description"
            as="textarea"
            value={formData.description}
            onChange={e => setFormData({...formData, description: e.target.value})}
            placeholder="Faculty description..."
          />

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
              {selectedFaculty ? 'Update Faculty' : 'Create Faculty'}
            </SubmitButton>
          </div>
        </form>
      </FormModal>

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onConfirm={handleDelete}
        onCancel={() => setIsDeleteOpen(false)}
        title="Delete Faculty"
        message={`Are you sure you want to delete ${selectedFaculty?.name}?`}
        confirmText="Delete"
        isLoading={isSaving}
      />
    </div>
  )
}
