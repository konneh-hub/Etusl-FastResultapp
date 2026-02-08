import { useState } from 'react'
import { useDispatch } from 'react-redux'

export default function GradeEntryForm({ courseId, onSubmit }) {
  const [formData, setFormData] = useState({
    ca_score: '',
    exam_score: '',
    comments: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    // Validation
    if (!formData.ca_score || !formData.exam_score) {
      setError('Both CA and Exam scores are required')
      return
    }

    const caScore = parseFloat(formData.ca_score)
    const examScore = parseFloat(formData.exam_score)

    if (caScore < 0 || caScore > 30 || examScore < 0 || examScore > 70) {
      setError('CA score must be 0-30, Exam score must be 0-70')
      return
    }

    try {
      setLoading(true)
      await onSubmit({
        course_id: courseId,
        ca_score: caScore,
        exam_score: examScore,
        comments: formData.comments
      })
    } catch (err) {
      setError(err.message || 'Failed to submit grades')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 max-w-2xl">
      <h2 className="text-2xl font-bold mb-6">Enter Student Grades</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded text-red-600">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              CA Score (0-30)
            </label>
            <input
              type="number"
              name="ca_score"
              min="0"
              max="30"
              step="0.5"
              value={formData.ca_score}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter CA score"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Exam Score (0-70)
            </label>
            <input
              type="number"
              name="exam_score"
              min="0"
              max="70"
              step="0.5"
              value={formData.exam_score}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter exam score"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Total Score
          </label>
          <input
            type="text"
            disabled
            value={
              formData.ca_score && formData.exam_score
                ? (parseFloat(formData.ca_score) + parseFloat(formData.exam_score)).toFixed(2)
                : '-'
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Comments
          </label>
          <textarea
            name="comments"
            value={formData.comments}
            onChange={handleChange}
            rows="4"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Add any comments or notes"
          />
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Submitting...' : 'Submit Grades'}
          </button>
          <button
            type="button"
            className="flex-1 bg-gray-500 text-white py-2 rounded-lg hover:bg-gray-600"
          >
            Cancel
          </button>
        </div>
      </div>
    </form>
  )
}
