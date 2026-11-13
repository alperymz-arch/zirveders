import { ReactNode } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { logout } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Layout({ children }: { children: ReactNode }) {
  const { setIsAuthenticated } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    setIsAuthenticated(false)
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Muhasebe Entegrasyon</h1>
        <nav className="app-nav">
          <NavLink to="/" end>Müşteriler</NavLink>
          <NavLink to="/invoices">Faturalar</NavLink>
          <NavLink to="/settings">Ayarlar</NavLink>
        </nav>
        <button className="btn btn-secondary" onClick={handleLogout}>
          Çıkış
        </button>
      </header>
      <main className="page-enter">{children}</main>
    </div>
  )
}
