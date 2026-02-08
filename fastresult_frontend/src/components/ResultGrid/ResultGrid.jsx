import { useState, useCallback, useRef } from 'react'
import { Download, RotateCcw, Save, Send } from 'lucide-react'
import toast from 'react-hot-toast'

/**
 * ResultGrid: Spreadsheet-style component for result entry
 * Features:
 * - Editable cells (CA, Exam marks)
 * - Auto-calculation (Total = CA + Exam)
 * - Copy/paste from Excel
 * - Validation (marks ≤ max_marks)
 * - Draft save and final submission
 */
export default function ResultGrid({
  students = [],
  courseId,
  onSaveDraft,
  onSubmit,
  isLoadingDraft = false,
  isLoadingSubmit = false,
  maxCAMarks = 30,
  maxExamMarks = 70
}) {
  const [data, setData] = useState(
    students.map(s => ({
      student_id: s.id,
      matric_number: s.matric_number,
      full_name: s.full_name,
      ca_marks: s.ca_marks || 0,
      exam_marks: s.exam_marks || 0,
      total_marks: (s.ca_marks || 0) + (s.exam_marks || 0),
      grade: calculateGrade((s.ca_marks || 0) + (s.exam_marks || 0)),
      comment: s.comment || ''
    }))
  )
  const [selectedCell, setSelectedCell] = useState(null)
  const gridRef = useRef(null)

  const maxTotalMarks = maxCAMarks + maxExamMarks

  /**
   * Simple grade calculation (A, B, C, D, F based on percentage)
   */
  function calculateGrade(total) {
    const percentage = (total / maxTotalMarks) * 100
    if (percentage >= 80) return 'A'
    if (percentage >= 70) return 'B'
    if (percentage >= 60) return 'C'
    if (percentage >= 50) return 'D'
    return 'F'
  }

  /**
   * Handle cell value change with validation
   */
  const handleCellChange = useCallback((index, field, value) => {
    const numValue = parseFloat(value) || 0

    // Validate marks don't exceed limits
    if (field === 'ca_marks' && numValue > maxCAMarks) {
      toast.error(`CA marks cannot exceed ${maxCAMarks}`)
      return
    }
    if (field === 'exam_marks' && numValue > maxExamMarks) {
      toast.error(`Exam marks cannot exceed ${maxExamMarks}`)
      return
    }

    setData(prev => {
      const updated = [...prev]
      updated[index] = { ...updated[index], [field]: numValue }

      // Auto-calculate total and grade
      if (field === 'ca_marks' || field === 'exam_marks') {
        updated[index].total_marks = updated[index].ca_marks + updated[index].exam_marks
        updated[index].grade = calculateGrade(updated[index].total_marks)
      }

      return updated
    })
  }, [maxCAMarks, maxExamMarks, maxTotalMarks])

  /**
   * Handle paste event from Excel
   * Format: Tab or space separated values
   */
  const handlePaste = (e) => {
    e.preventDefault()
    const clipboardData = e.clipboardData.getData('text')
    const rows = clipboardData.split('\n').filter(r => r.trim())

    rows.forEach((row, rowIndex) => {
      const values = row.split(/[\t ]/).filter(v => v.trim())
      if (values.length >= 2 && rowIndex < data.length) {
        const caMarks = parseFloat(values[0]) || 0
        const examMarks = parseFloat(values[1]) || 0

        if (caMarks > maxCAMarks || examMarks > maxExamMarks) {
          toast.error(`Row ${rowIndex + 1}: Marks exceed limits`)
          return
        }

        handleCellChange(rowIndex, 'ca_marks', caMarks)
        handleCellChange(rowIndex, 'exam_marks', examMarks)
      }
    })

    toast.success(`Pasted data from ${rows.length} rows`)
  }

  /**
   * Reset all data
   */
  const handleReset = () => {
    setData(students.map(s => ({
      student_id: s.id,
      matric_number: s.matric_number,
      full_name: s.full_name,
      ca_marks: s.ca_marks || 0,
      exam_marks: s.exam_marks || 0,
      total_marks: (s.ca_marks || 0) + (s.exam_marks || 0),
      grade: calculateGrade((s.ca_marks || 0) + (s.exam_marks || 0)),
      comment: s.comment || ''
    })))
    toast.success('Data reset')
  }

  /**
   * Save as draft
   */
  const handleSaveDraft = () => {
    if (onSaveDraft) {
      onSaveDraft(courseId, data)
    }
  }

  /**
   * Submit results for grading
   */
  const handleSubmit = () => {
    if (onSubmit) {
      onSubmit(courseId, data)
    }
  }

  return (
    <div className="w-full">
      {/* Toolbar */}
      <div className="mb-4 flex gap-2 flex-wrap">
        <button
          onClick={handleReset}
          className="flex items-center gap-2 px-3 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition"
        >
          <RotateCcw size={16} /> Reset
        </button>
        <button
          onClick={handleSaveDraft}
          disabled={isLoadingDraft}
          className="flex items-center gap-2 px-3 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition disabled:opacity-50"
        >
          {isLoadingDraft ? 'Saving...' : <>
            <Save size={16} /> Save Draft
          </>}
        </button>
        <button
          onClick={handleSubmit}
          disabled={isLoadingSubmit}
          className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition disabled:opacity-50"
        >
          {isLoadingSubmit ? 'Submitting...' : <>
            <Send size={16} /> Submit Results
          </>}
        </button>
      </div>

      {/* Instructions */}
      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
        <strong>Tips:</strong> Click cells to edit | Paste CA and Exam marks from Excel in tab-separated format | Max CA: {maxCAMarks}, Max Exam: {maxExamMarks}
      </div>

      {/* Spreadsheet */}
      <div
        ref={gridRef}
        className="overflow-x-auto border rounded-lg bg-white"
        onPaste={handlePaste}
      >
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-gray-100 border-b">
              <th className="px-3 py-2 text-left font-semibold text-gray-700 border-r w-16">#</th>
              <th className="px-3 py-2 text-left font-semibold text-gray-700 border-r min-w-[120px]">
                Matric
              </th>
              <th className="px-3 py-2 text-left font-semibold text-gray-700 border-r min-w-[180px]">
                Student Name
              </th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700 border-r w-24">
                CA ({maxCAMarks})
              </th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700 border-r w-24">
                Exam ({maxExamMarks})
              </th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700 border-r w-24">
                Total ({maxTotalMarks})
              </th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700 border-r w-16">
                Grade
              </th>
              <th className="px-3 py-2 text-left font-semibold text-gray-700 min-w-[150px]">
                Comment
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={row.student_id} className="border-b hover:bg-blue-50 transition">
                <td className="px-3 py-2 text-gray-600 border-r">{idx + 1}</td>
                <td className="px-3 py-2 text-gray-800 border-r font-mono text-sm">
                  {row.matric_number}
                </td>
                <td className="px-3 py-2 text-gray-800 border-r">{row.full_name}</td>

                {/* CA Marks - Editable */}
                <td className="px-3 py-2 border-r">
                  <input
                    type="number"
                    min="0"
                    max={maxCAMarks}
                    value={row.ca_marks}
                    onChange={e => handleCellChange(idx, 'ca_marks', e.target.value)}
                    onClick={() => setSelectedCell(`${idx}-ca`)}
                    className="w-full text-center border rounded p-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </td>

                {/* Exam Marks - Editable */}
                <td className="px-3 py-2 border-r">
                  <input
                    type="number"
                    min="0"
                    max={maxExamMarks}
                    value={row.exam_marks}
                    onChange={e => handleCellChange(idx, 'exam_marks', e.target.value)}
                    onClick={() => setSelectedCell(`${idx}-exam`)}
                    className="w-full text-center border rounded p-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </td>

                {/* Total - Auto-calculated, Read-only */}
                <td className="px-3 py-2 border-r text-center font-semibold bg-gray-50">
                  {row.total_marks}
                </td>

                {/* Grade - Auto-calculated */}
                <td className={`px-3 py-2 border-r text-center font-bold rounded
                  ${row.grade === 'A' ? 'bg-green-100 text-green-800' :
                    row.grade === 'B' ? 'bg-green-50 text-green-700' :
                    row.grade === 'C' ? 'bg-yellow-50 text-yellow-700' :
                    row.grade === 'D' ? 'bg-orange-50 text-orange-700' :
                    'bg-red-100 text-red-800'
                  }`}
                >
                  {row.grade}
                </td>

                {/* Comment - Editable */}
                <td className="px-3 py-2">
                  <input
                    type="text"
                    value={row.comment}
                    onChange={e => handleCellChange(idx, 'comment', e.target.value)}
                    placeholder="Add note..."
                    className="w-full border rounded p-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Stats */}
      <div className="mt-4 grid grid-cols-4 gap-4 text-sm">
        <div className="p-3 bg-blue-50 rounded">
          <div className="text-gray-600">Total Students</div>
          <div className="text-2xl font-bold text-blue-600">{data.length}</div>
        </div>
        <div className="p-3 bg-green-50 rounded">
          <div className="text-gray-600">Grade A</div>
          <div className="text-2xl font-bold text-green-600">
            {data.filter(d => d.grade === 'A').length}
          </div>
        </div>
        <div className="p-3 bg-yellow-50 rounded">
          <div className="text-gray-600">Avg Total</div>
          <div className="text-2xl font-bold text-yellow-600">
            {(data.reduce((sum, d) => sum + d.total_marks, 0) / data.length).toFixed(1)}
          </div>
        </div>
        <div className="p-3 bg-red-50 rounded">
          <div className="text-gray-600">Grade F</div>
          <div className="text-2xl font-bold text-red-600">
            {data.filter(d => d.grade === 'F').length}
          </div>
        </div>
      </div>
    </div>
  )
}
