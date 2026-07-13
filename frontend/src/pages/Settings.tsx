import { FormEvent, useEffect, useState } from 'react'
import { apiFetch } from '../api/client'
import Layout from '../components/Layout'

interface AccountingSettings {
  configured: boolean
  api_key_preview: string | null
}

export default function Settings() {
  const [settings, setSettings] = useState<AccountingSettings | null>(null)
  const [apiKey, setApiKey] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  function loadSettings() {
    apiFetch('/settings/accounting')
      .then(setSettings)
      .catch(() => setError('Ayarlar okunamadı (yönetici yetkisi gerekebilir)'))
  }

  useEffect(loadSettings, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setSaving(true)
    try {
      const updated = await apiFetch('/settings/accounting', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey }),
      })
      setSettings(updated)
      setApiKey('')
      setSuccess('ZirAPI anahtarı kaydedildi.')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Layout>
      <h1>Muhasebe Ayarları</h1>
      <p>
        Zirve entegrasyonu ZirAPI üzerinden çalışır. Kendi ZirAPI hesabınızdan
        aldığınız API anahtarını aşağıya girin.
      </p>

      <p>
        Durum:{' '}
        {settings === null
          ? 'yükleniyor...'
          : settings.configured
            ? `Tanımlı (${settings.api_key_preview})`
            : 'Tanımlı değil'}
      </p>

      <form className="card" onSubmit={handleSubmit}>
        <input
          type="password"
          placeholder="ZirAPI anahtarı"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          required
        />
        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving ? 'Kaydediliyor...' : 'Kaydet'}
        </button>
        {error && <p className="alert alert-error">{error}</p>}
        {success && <p className="alert alert-success">{success}</p>}
      </form>
    </Layout>
  )
}
