export default function ResultCard({ result, onClick }) {
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
    <div 
      className="bg-white rounded-lg shadow p-6 hover:shadow-lg cursor-pointer transition-shadow"
      onClick={onClick}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-semibold text-lg text-gray-900">{result.course_name}</h3>
          <p className="text-sm text-gray-600">{result.course_code}</p>
          <div className="mt-4 grid grid-cols-2 gap-2">
            <div>
              <p className="text-xs text-gray-600">Exam Score</p>
              <p className="font-bold text-lg">{result.exam_score || '-'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600">CA Score</p>
              <p className="font-bold text-lg">{result.ca_score || '-'}</p>
            </div>
          </div>
        </div>
        <div className={`px-4 py-2 rounded-lg font-bold text-lg ${getGradeColor(result.grade)}`}>
          {result.grade || 'P'}
        </div>
      </div>
      <div className="mt-4 pt-4 border-t">
        <p className="text-sm">
          <span className="text-gray-600">Total Score:</span>
          <span className="font-bold ml-2">{result.total_score || '-'}</span>
        </p>
      </div>
    </div>
  )
}
