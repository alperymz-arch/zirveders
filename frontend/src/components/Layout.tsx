import { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
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
          <Link to="/">Müşteriler</Link>
          <Link to="/invoices">Faturalar</Link>
          <Link to="/settings">Ayarlar</Link>
        </nav>
        <button className="btn btn-secondary" onClick={handleLogout}>
          Çıkış
        </button>
      </header>
      {children}
    </div>
  )
}
