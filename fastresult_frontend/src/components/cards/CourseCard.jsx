export default function CourseCard({ course, onClick }) {
  return (
    <div 
      className="bg-white rounded-lg shadow p-6 hover:shadow-lg cursor-pointer transition-shadow"
      onClick={onClick}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-semibold text-lg text-gray-900">{course.name}</h3>
          <p className="text-sm text-gray-600">{course.code}</p>
          <div className="mt-4 space-y-2">
            <p className="text-sm">
              <span className="text-gray-600">Lecturer:</span>
              <span className="font-medium ml-2">{course.lecturer}</span>
            </p>
            <p className="text-sm">
              <span className="text-gray-600">Credits:</span>
              <span className="font-medium ml-2">{course.credits}</span>
            </p>
            <p className="text-sm">
              <span className="text-gray-600">Students:</span>
              <span className="font-medium ml-2">{course.students}</span>
            </p>
          </div>
        </div>
        <div className="text-2xl">{course.icon || '📚'}</div>
      </div>
      <button className="mt-4 w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600">
        View Details
      </button>
    </div>
  )
}
