import React from 'react'

export default function DashboardLayout({ sidebar, header, children }) {
  return (
    <div className="dashboard-layout">
      {sidebar && <aside className="sidebar">{sidebar}</aside>}
      <main className="main-content">
        {header && <div className="topbar">{header}</div>}
        <div className="content-area">
          {children}
        </div>
      </main>
    </div>
  )
}
