export default function ResultsTable({ data, loading, onRowClick }) {
  if (loading) {
    return <div className="text-center py-8">Loading results...</div>
  }

  const getGradeColor = (grade) => {
    const colors = {
      'A': 'bg-green-100 text-green-800',
      'B': 'bg-blue-100 text-blue-800',
      'C': 'bg-yellow-100 text-yellow-800',
      'D': 'bg-orange-100 text-orange-800',
      'F': 'bg-red-100 text-red-800'
    }
    return colors[grade] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Course</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Code</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">CA</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Exam</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Total</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Grade</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Points</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Credits</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {data.map((result) => (
            <tr 
              key={result.id}
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() => onRowClick?.(result)}
            >
              <td className="px-6 py-4 text-sm font-medium text-gray-900">{result.course_name}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{result.course_code}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{result.ca_score || '-'}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{result.exam_score || '-'}</td>
              <td className="px-6 py-4 text-sm font-medium">{result.total_score || '-'}</td>
              <td className="px-6 py-4">
                <span className={`px-3 py-1 rounded font-bold ${getGradeColor(result.grade)}`}>
                  {result.grade || '-'}
                </span>
              </td>
              <td className="px-6 py-4 text-sm font-medium">{result.grade_points || '-'}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{result.credits || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
