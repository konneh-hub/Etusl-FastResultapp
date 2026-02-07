import React from 'react'

export default function DataTable({ columns, data, loading, onRowClick }) {
  if (loading) return <div className="table-loading">Loading...</div>

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map(column => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data && data.length > 0 ? (
            data.map((row, index) => (
              <tr 
                key={row.id || index}
                onClick={() => onRowClick && onRowClick(row)}
              >
                {columns.map(column => (
                  <td key={column.key}>
                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={columns.length} style={{ textAlign: 'center' }}>
                No data available
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
