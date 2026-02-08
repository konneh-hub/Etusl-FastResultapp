import React from 'react'
import toast from 'react-hot-toast'

/**
 * CRUDTable: Reusable table component with add/edit/delete actions
 * Props:
 * - title: page title
 * - columns: array of {key, label, render?(optional)}
 * - data: array of rows
 * - onAdd: callback when add button clicked
 * - onEdit: callback when edit button clicked
 * - onDelete: callback when delete button clicked
 * - loading: boolean to show loading state
 * - pagination: {current, total, limit} for pagination info
 * - onPageChange: callback(page) when pagination changes
 */
export default function CRUDTable({
  title,
  columns,
  data = [],
  onAdd,
  onEdit,
  onDelete,
  loading = false,
  pagination = null,
  onPageChange = null
}) {
  const handleDelete = (row) => {
    if (window.confirm(`Are you sure you want to delete this ${title.slice(0, -1).toLowerCase()}?`)) {
      onDelete?.(row)
    }
  }

  return (
    <div className="crud-table">
      <div className="crud-header">
        <h2>{title}</h2>
        <button className="btn btn-primary" onClick={onAdd}>
          + Add New
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : data.length === 0 ? (
        <div className="empty-state">
          <p>No {title.toLowerCase()} found</p>
          <button className="btn btn-primary" onClick={onAdd}>
            Create one now
          </button>
        </div>
      ) : (
        <>
          <table className="table">
            <thead>
              <tr>
                {columns.map(col => (
                  <th key={col.key}>{col.label}</th>
                ))}
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={row.id || idx}>
                  {columns.map(col => (
                    <td key={col.key}>
                      {col.render ? col.render(row) : row[col.key]}
                    </td>
                  ))}
                  <td className="actions">
                    <button
                      className="btn btn-sm btn-info"
                      onClick={() => onEdit?.(row)}
                      title="Edit"
                    >
                      ✎
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(row)}
                      title="Delete"
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {pagination && (
            <div className="pagination">
              <button
                disabled={pagination.current === 1}
                onClick={() => onPageChange?.(pagination.current - 1)}
              >
                Previous
              </button>
              <span>
                Page {pagination.current} of {Math.ceil(pagination.total / pagination.limit)}
              </span>
              <button
                disabled={pagination.current >= Math.ceil(pagination.total / pagination.limit)}
                onClick={() => onPageChange?.(pagination.current + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
