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
  status: string
  error_message: string | null
  created_at: string
}

export default function Invoices() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [customerId, setCustomerId] = useState('')
  const [referenceNo, setReferenceNo] = useState('')
  const [lines, setLines] = useState<InvoiceLine[]>([{ aciklama: '', tutar: 0 }])
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  function loadCustomers() {
    apiFetch('/accounting/customers').then(setCustomers).catch(() => setCustomers([]))
  }

  function loadInvoices() {
    apiFetch('/accounting/invoices').then(setInvoices).catch(() => setInvoices([]))
  }

  useEffect(() => {
    loadCustomers()
    loadInvoices()
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
        {invoices.map((inv) => (
          <li key={inv.id}>
            {inv.reference_no} — {inv.customer_name} — {inv.total_amount} {inv.currency} —{' '}
            {inv.status === 'sent' ? 'Gönderildi' : 'Hata'}
            {inv.status === 'failed' && inv.error_message ? `: ${inv.error_message}` : ''}
          </li>
        ))}
      </ul>
    </div>
  )
}
