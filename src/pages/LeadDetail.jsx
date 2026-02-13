import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { formatDateIST } from '../utils/date'

export default function LeadDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [lead, setLead] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    let cancelled = false
    api.getLead(id)
      .then((data) => { if (!cancelled) setLead(data) })
      .catch((e) => { if (!cancelled) setError(e.message) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [id])

  const handleDelete = async () => {
    if (!window.confirm('Delete this lead?')) return
    setDeleting(true)
    setError(null)
    try {
      await api.deleteLead(id)
      navigate('/')
    } catch (e) {
      setError(e.message)
    } finally {
      setDeleting(false)
    }
  }

  if (loading) return <p className="caption">Loading…</p>
  if (error && !lead) return <div className="alert alert-error">{error}</div>
  if (!lead) return null

  return (
    <div className="lead-detail-page">
      <p style={{ marginBottom: 24 }}>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => navigate('/')}>← Back to leads</button>
      </p>
      <h1 className="h2">Lead details</h1>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="card lead-detail-card">
        <section className="lead-detail-section">
          <h3 className="h4 lead-detail-section-title">Identity</h3>
          <dl className="lead-detail-dl">
            <div className="lead-detail-row">
              <dt>Tracking ID</dt>
              <dd><code>{lead.tracking_id}</code></dd>
            </div>
            <div className="lead-detail-row">
              <dt>Campaign name</dt>
              <dd>{lead.campaign_name || '—'}</dd>
            </div>
            <div className="lead-detail-row">
              <dt>Email</dt>
              <dd>{lead.email || '—'}</dd>
            </div>
          </dl>
        </section>
        <section className="lead-detail-section">
          <h3 className="h4 lead-detail-section-title">Status &amp; timestamps</h3>
          <dl className="lead-detail-dl">
            <div className="lead-detail-row">
              <dt>Opened</dt>
              <dd><span className="status-opened">Opened</span></dd>
            </div>
            <div className="lead-detail-row">
              <dt>Created at (IST)</dt>
              <dd className="lead-detail-value-muted">{formatDateIST(lead.created_at)}</dd>
            </div>
            <div className="lead-detail-row">
              <dt>First click at (IST)</dt>
              <dd className="lead-detail-value-muted">{formatDateIST(lead.first_click_at)}</dd>
            </div>
          </dl>
        </section>
        <div className="lead-detail-actions">
          <button type="button" className="btn btn-danger" onClick={handleDelete} disabled={deleting}>{deleting ? 'Deleting…' : 'Delete lead'}</button>
        </div>
      </div>
    </div>
  )
}
