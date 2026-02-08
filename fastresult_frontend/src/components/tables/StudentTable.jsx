export default function StudentTable({ data, loading, onRowClick }) {
  if (loading) {
    return <div className="text-center py-8">Loading students...</div>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Name</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Matric No</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Email</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Program</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {data.map((student) => (
            <tr 
              key={student.id}
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() => onRowClick?.(student)}
            >
              <td className="px-6 py-4 text-sm font-medium text-gray-900">
                {student.first_name} {student.last_name}
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">{student.matric_number}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{student.email}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{student.program}</td>
              <td className="px-6 py-4">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  student.status === 'active' 
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {student.status}
                </span>
              </td>
              <td className="px-6 py-4 text-sm">
                <button className="text-blue-600 hover:text-blue-900">View</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
