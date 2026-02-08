import React from 'react'

export default function Table({columns, data, onRowClick}){
  return (
    <table className="srms-table">
      <thead>
        <tr>{columns.map(c => <th key={c.key}>{c.title}</th>)}</tr>
      </thead>
      <tbody>
        {data.map((row,i) => (
          <tr key={i} onClick={()=>onRowClick && onRowClick(row)}>
            {columns.map(c => <td key={c.key}>{row[c.key]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
