export default function ApprovalTable({ data, loading, onApprove, onReject }) {
  if (loading) {
    return <div className="text-center py-8">Loading approvals...</div>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Submission</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Course</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Lecturer</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Students</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {data.map((approval) => (
            <tr key={approval.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 text-sm font-medium text-gray-900">
                {approval.submission_id}
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">{approval.course_name}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{approval.lecturer_name}</td>
              <td className="px-6 py-4 text-sm text-gray-600">{approval.students_count}</td>
              <td className="px-6 py-4">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  approval.status === 'pending'
                    ? 'bg-yellow-100 text-yellow-800'
                    : approval.status === 'approved'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {approval.status}
                </span>
              </td>
              <td className="px-6 py-4 text-sm space-x-2">
                {approval.status === 'pending' && (
                  <>
                    <button 
                      onClick={() => onApprove?.(approval.id)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Approve
                    </button>
                    <button 
                      onClick={() => onReject?.(approval.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Reject
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
