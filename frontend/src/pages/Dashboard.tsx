import { FormEvent, useEffect, useState } from 'react'
import Layout from '../components/Layout'
import { apiFetch } from '../api/client'

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

  function loadCustomers() {
    apiFetch('/accounting/customers').then(setCustomers).catch(() => setCustomers([]))
  }

  useEffect(loadCustomers, [])

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
    <Layout>
      <h2>Müşteriler</h2>
      {error && <p className="alert alert-error">{error}</p>}
      <ul className="list card">
        {customers.map((c) =>
          editingId === c.external_id ? (
            <li className="list-item" key={c.external_id}>
              <input value={editName} onChange={(e) => setEditName(e.target.value)} />
              <input
                value={editTaxNumber}
                onChange={(e) => setEditTaxNumber(e.target.value)}
                placeholder="VKN/TCKN"
              />
              <div className="list-item-actions">
                <button className="btn btn-primary" onClick={() => handleUpdate(c.external_id)}>
                  Kaydet
                </button>
                <button className="btn btn-secondary" onClick={() => setEditingId(null)}>
                  Vazgeç
                </button>
              </div>
            </li>
          ) : (
            <li className="list-item" key={c.external_id}>
              <span className="list-item-main">
                {c.name} — {c.balance} TL
              </span>
              <button className="btn btn-secondary" onClick={() => startEdit(c)}>
                Düzenle
              </button>
            </li>
          ),
        )}
      </ul>

      <h3>Yeni Müşteri</h3>
      <form className="card" onSubmit={handleCreate}>
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
        <button className="btn btn-primary" type="submit">
          Ekle
        </button>
      </form>
    </Layout>
  )
}
