import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiFetch, logout } from '../api/client'
import { useAuth } from '../context/AuthContext'

interface Customer {
  external_id: string
  name: string
  balance: number
}

export default function Dashboard() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const { setIsAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    apiFetch('/accounting/customers')
      .then(setCustomers)
      .catch(() => setCustomers([]))
  }, [])

  function handleLogout() {
    logout()
    setIsAuthenticated(false)
    navigate('/login')
  }

  return (
    <div>
      <header>
        <h1>Muhasebe Entegrasyon</h1>
        <Link to="/settings">Ayarlar</Link>
        <button onClick={handleLogout}>Çıkış</button>
      </header>
      <h2>Müşteriler</h2>
      <ul>
        {customers.map((c) => (
          <li key={c.external_id}>
            {c.name} — {c.balance} TL
          </li>
        ))}
      </ul>
    </div>
  )
}
