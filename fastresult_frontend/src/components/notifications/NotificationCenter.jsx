import React from 'react'

export default function NotificationCenter({ notifications = [], onClose }) {
  return (
    <div className="notification-center">
      <h2>Notifications</h2>
      <div className="notifications-list">
        {notifications && notifications.length > 0 ? (
          notifications.map((notif, index) => (
            <div key={index} className={`notification ${notif.type}`}>
              <p>{notif.message}</p>
            </div>
          ))
        ) : (
          <p>No notifications</p>
        )}
      </div>
    </div>
  )
}
