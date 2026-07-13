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
    <div>
      <header>
        <h1>Muhasebe Entegrasyon</h1>
        <nav>
          <Link to="/">Müşteriler</Link>
          <Link to="/invoices">Faturalar</Link>
          <Link to="/settings">Ayarlar</Link>
        </nav>
        <button onClick={handleLogout}>Çıkış</button>
      </header>
      {children}
    </div>
  )
}
