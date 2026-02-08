import React from 'react'
import { useAuth } from '../hooks/useAuth'

export default function Header(){
  const { user, logout } = useAuth()
  return (
    <header className="header">
      <div className="left"> <h3>SRMS</h3> </div>
      <div className="right">
        <button onClick={logout}>Logout</button>
        <span className="user">{user ? user.first_name : 'Guest'}</span>
      </div>
    </header>
  )
}
