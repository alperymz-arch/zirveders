import { FormEvent, useEffect, useState } from 'react'
import { apiFetch } from '../api/client'

interface Customer {
  external_id: string
  name: string
  balance: number
}

interface InvoiceLine {
  aciklama: string
  tutar: number
}

interface Invoice {
  id: number
  reference_no: string
  customer_name: string
  total_amount: number
  currency: string
  lines: InvoiceLine[]
  status: string
  error_message: string | null
  created_at: string
  deleted_at: string | null
}

interface CurrentUser {
  role: string
}

export default function Invoices() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [trash, setTrash] = useState<Invoice[]>([])
  const [isAdmin, setIsAdmin] = useState(false)
  const [customerId, setCustomerId] = useState('')
  const [referenceNo, setReferenceNo] = useState('')
  const [lines, setLines] = useState<InvoiceLine[]>([{ aciklama: '', tutar: 0 }])
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [editingInvoiceId, setEditingInvoiceId] = useState<number | null>(null)
  const [editingLines, setEditingLines] = useState<InvoiceLine[]>([])

  function loadCustomers() {
    apiFetch('/accounting/customers').then(setCustomers).catch(() => setCustomers([]))
  }

  function loadInvoices() {
    apiFetch('/accounting/invoices').then(setInvoices).catch(() => setInvoices([]))
  }

  function loadTrash() {
    apiFetch('/accounting/invoices/trash').then(setTrash).catch(() => setTrash([]))
  }

  useEffect(() => {
    loadCustomers()
    loadInvoices()
    apiFetch('/users/me')
      .then((me: CurrentUser) => {
        setIsAdmin(me.role === 'admin')
        if (me.role === 'admin') loadTrash()
      })
      .catch(() => setIsAdmin(false))
  }, [])

  function updateLine(index: number, field: keyof InvoiceLine, value: string) {
    setLines((prev) =>
      prev.map((line, i) =>
        i === index ? { ...line, [field]: field === 'tutar' ? Number(value) : value } : line,
      ),
    )
  }

  function addLine() {
    setLines((prev) => [...prev, { aciklama: '', tutar: 0 }])
  }

  function removeLine(index: number) {
    setLines((prev) => prev.filter((_, i) => i !== index))
  }

  const total = lines.reduce((sum, line) => sum + (Number(line.tutar) || 0), 0)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setSaving(true)
    try {
      await apiFetch('/accounting/invoices', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_external_id: customerId,
          reference_no: referenceNo || null,
          lines,
        }),
      })
      setSuccess('Fatura muhasebe programına gönderildi.')
      setReferenceNo('')
      setLines([{ aciklama: '', tutar: 0 }])
      loadInvoices()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  async function handleCancel(id: number) {
    setError(null)
    try {
      await apiFetch(`/accounting/invoices/${id}/cancel`, { method: 'POST' })
      loadInvoices()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm('Fatura silinenler kutusuna taşınacak, emin misin?')) return
    setError(null)
    try {
      await apiFetch(`/accounting/invoices/${id}`, { method: 'DELETE' })
      loadInvoices()
      loadTrash()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  async function handleRestore(id: number) {
    setError(null)
    try {
      await apiFetch(`/accounting/invoices/${id}/restore`, { method: 'POST' })
      loadInvoices()
      loadTrash()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  async function handlePurge(id: number) {
    if (!window.confirm('Bu fatura kalıcı olarak silinecek, geri alınamaz. Emin misin?')) return
    setError(null)
    try {
      await apiFetch(`/accounting/invoices/${id}/purge`, { method: 'DELETE' })
      loadTrash()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  function startEditLines(inv: Invoice) {
    setEditingInvoiceId(inv.id)
    setEditingLines(inv.lines.map((line) => ({ ...line })))
  }

  function updateEditingLine(index: number, field: keyof InvoiceLine, value: string) {
    setEditingLines((prev) =>
      prev.map((line, i) =>
        i === index ? { ...line, [field]: field === 'tutar' ? Number(value) : value } : line,
      ),
    )
  }

  function addEditingLine() {
    setEditingLines((prev) => [...prev, { aciklama: '', tutar: 0 }])
  }

  function removeEditingLine(index: number) {
    setEditingLines((prev) => prev.filter((_, i) => i !== index))
  }

  async function handleSaveLines(id: number) {
    setError(null)
    try {
      await apiFetch(`/accounting/invoices/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lines: editingLines }),
      })
      setEditingInvoiceId(null)
      loadInvoices()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  function statusLabel(inv: Invoice) {
    if (inv.status === 'sent') return 'Gönderildi'
    if (inv.status === 'cancelled') return 'İptal edildi'
    return `Hata${inv.error_message ? `: ${inv.error_message}` : ''}`
  }

  return (
    <div>
      <h1>Fatura Girişi</h1>

      <form onSubmit={handleSubmit}>
        <select value={customerId} onChange={(e) => setCustomerId(e.target.value)} required>
          <option value="">Müşteri seçin</option>
          {customers.map((c) => (
            <option key={c.external_id} value={c.external_id}>
              {c.name}
            </option>
          ))}
        </select>

        <input
          type="text"
          placeholder="Referans no (boş bırakılırsa otomatik oluşturulur)"
          value={referenceNo}
          onChange={(e) => setReferenceNo(e.target.value)}
        />

        <h2>Kalemler</h2>
        {lines.map((line, i) => (
          <div key={i}>
            <input
              type="text"
              placeholder="Açıklama"
              value={line.aciklama}
              onChange={(e) => updateLine(i, 'aciklama', e.target.value)}
              required
            />
            <input
              type="number"
              step="0.01"
              min="0.01"
              placeholder="Tutar"
              value={line.tutar || ''}
              onChange={(e) => updateLine(i, 'tutar', e.target.value)}
              required
            />
            {lines.length > 1 && (
              <button type="button" onClick={() => removeLine(i)}>
                Sil
              </button>
            )}
          </div>
        ))}
        <button type="button" onClick={addLine}>
          + Kalem Ekle
        </button>

        <p>Toplam: {total.toFixed(2)} TL</p>

        <button type="submit" disabled={saving}>
          {saving ? 'Gönderiliyor...' : 'Faturayı Gönder'}
        </button>
        {error && <p role="alert">{error}</p>}
        {success && <p>{success}</p>}
      </form>

      <h2>Gönderilen Faturalar</h2>
      <ul>
        {invoices.map((inv) =>
          editingInvoiceId === inv.id ? (
            <li key={inv.id}>
              <strong>{inv.reference_no}</strong> kalemlerini düzenle:
              {editingLines.map((line, i) => (
                <div key={i}>
                  <input
                    type="text"
                    placeholder="Açıklama"
                    value={line.aciklama}
                    onChange={(e) => updateEditingLine(i, 'aciklama', e.target.value)}
                  />
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="Tutar"
                    value={line.tutar || ''}
                    onChange={(e) => updateEditingLine(i, 'tutar', e.target.value)}
                  />
                  {editingLines.length > 1 && (
                    <button onClick={() => removeEditingLine(i)}>Sil</button>
                  )}
                </div>
              ))}
              <button onClick={addEditingLine}>+ Kalem Ekle</button>
              <button onClick={() => handleSaveLines(inv.id)}>Kaydet ve Yeniden Gönder</button>
              <button onClick={() => setEditingInvoiceId(null)}>Vazgeç</button>
            </li>
          ) : (
            <li key={inv.id}>
              {inv.reference_no} — {inv.customer_name} — {inv.total_amount} {inv.currency} —{' '}
              {statusLabel(inv)}{' '}
              {inv.status !== 'cancelled' && (
                <button onClick={() => handleCancel(inv.id)}>İptal Et</button>
              )}
              {inv.status === 'failed' && (
                <button onClick={() => startEditLines(inv)}>Kalemleri Düzenle</button>
              )}
              {isAdmin && <button onClick={() => handleDelete(inv.id)}>Sil</button>}
            </li>
          ),
        )}
      </ul>

      {isAdmin && (
        <>
          <h2>Silinenler</h2>
          <ul>
            {trash.map((inv) => (
              <li key={inv.id}>
                {inv.reference_no} — {inv.customer_name} — {inv.total_amount} {inv.currency}{' '}
                <button onClick={() => handleRestore(inv.id)}>Geri Yükle</button>
                <button onClick={() => handlePurge(inv.id)}>Kalıcı Olarak Sil</button>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}
