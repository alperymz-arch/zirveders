import { FormEvent, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiFetch, logout } from '../api/client'
import { useAuth } from '../context/AuthContext'

interface Customer {
  external_id: string
  name: string
  tax_number: string | null
  balance: number
}

export default function Dashboard() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editName, setEditName] = useState('')
  const [editTaxNumber, setEditTaxNumber] = useState('')
  const [newName, setNewName] = useState('')
  const [newTaxNumber, setNewTaxNumber] = useState('')
  const [newExternalId, setNewExternalId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const { setIsAuthenticated } = useAuth()
  const navigate = useNavigate()

  function loadCustomers() {
    apiFetch('/accounting/customers').then(setCustomers).catch(() => setCustomers([]))
  }

  useEffect(loadCustomers, [])

  function handleLogout() {
    logout()
    setIsAuthenticated(false)
    navigate('/login')
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await apiFetch('/accounting/customers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          external_id: newExternalId || null,
          name: newName,
          tax_number: newTaxNumber || null,
        }),
      })
      setNewName('')
      setNewTaxNumber('')
      setNewExternalId('')
      loadCustomers()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  function startEdit(c: Customer) {
    setEditingId(c.external_id)
    setEditName(c.name)
    setEditTaxNumber(c.tax_number ?? '')
  }

  async function handleUpdate(externalId: string) {
    setError(null)
    try {
      await apiFetch(`/accounting/customers/${externalId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: editName, tax_number: editTaxNumber || null }),
      })
      setEditingId(null)
      loadCustomers()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <div>
      <header>
        <h1>Muhasebe Entegrasyon</h1>
        <Link to="/invoices">Faturalar</Link>
        <Link to="/settings">Ayarlar</Link>
        <button onClick={handleLogout}>Çıkış</button>
      </header>

      <h2>Müşteriler</h2>
      {error && <p role="alert">{error}</p>}
      <ul>
        {customers.map((c) =>
          editingId === c.external_id ? (
            <li key={c.external_id}>
              <input value={editName} onChange={(e) => setEditName(e.target.value)} />
              <input
                value={editTaxNumber}
                onChange={(e) => setEditTaxNumber(e.target.value)}
                placeholder="VKN/TCKN"
              />
              <button onClick={() => handleUpdate(c.external_id)}>Kaydet</button>
              <button onClick={() => setEditingId(null)}>Vazgeç</button>
            </li>
          ) : (
            <li key={c.external_id}>
              {c.name} — {c.balance} TL
              <button onClick={() => startEdit(c)}>Düzenle</button>
            </li>
          ),
        )}
      </ul>

      <h3>Yeni Müşteri</h3>
      <form onSubmit={handleCreate}>
        <input
          type="text"
          placeholder="Müşteri adı"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="VKN/TCKN (opsiyonel)"
          value={newTaxNumber}
          onChange={(e) => setNewTaxNumber(e.target.value)}
        />
        <input
          type="text"
          placeholder="Müşteri kodu (boş bırakılırsa otomatik)"
          value={newExternalId}
          onChange={(e) => setNewExternalId(e.target.value)}
        />
        <button type="submit">Ekle</button>
      </form>
    </div>
  )
}
