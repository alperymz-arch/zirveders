import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const { setIsAuthenticated } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await login(email, password)
      setIsAuthenticated(true)
      navigate('/')
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <div className="login-page">
      <div className="login-brand">
        <svg
          className="login-brand-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          aria-hidden="true"
        >
          <path
            d="M6 2.5h9.5L19 6v15a.5.5 0 0 1-.5.5h-12A.5.5 0 0 1 6 21V2.5Z"
            strokeLinejoin="round"
          />
          <path d="M15.5 2.5V6H19" strokeLinejoin="round" />
          <path d="M9 11h6M9 14h6M9 17h3.5" strokeLinecap="round" />
        </svg>
        <h1>Muhasebe Entegrasyon</h1>
        <p>Zirve ile webapp arasında müşteri ve fatura senkronizasyonunu tek bir yerden yönet.</p>
        <div className="login-brand-badges">
          <span className="login-brand-badge">ZirAPI entegrasyonu</span>
          <span className="login-brand-badge">Toplu fatura</span>
          <span className="login-brand-badge">PDF'ten okuma</span>
        </div>
      </div>

      <div className="login-form-panel">
        <form onSubmit={handleSubmit}>
          <h2>Giriş Yap</h2>
          <p className="lede">Hesabınla devam etmek için bilgilerini gir.</p>
          <input
            type="email"
            placeholder="E-posta"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Şifre"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button className="btn btn-primary" type="submit">
            Giriş
          </button>
          {error && <p className="alert alert-error">{error}</p>}
        </form>
      </div>
    </div>
  )
}
