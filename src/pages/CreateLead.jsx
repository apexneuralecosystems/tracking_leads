import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function CreateLead() {
  const navigate = useNavigate()
  const [mode, setMode] = useState('lead_id')
  const [lead_id, setLeadId] = useState('')
  const [email, setEmail] = useState('')
  const [campaign_name, setCampaignName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    const body = mode === 'lead_id'
      ? { lead_id: lead_id.trim(), campaign_name: campaign_name.trim() || undefined }
      : { email: email.trim(), campaign_name: campaign_name.trim() || undefined }
    if (mode === 'lead_id' && !lead_id.trim()) { setError('Enter a tracking ID (lead_id).'); return }
    if (mode === 'email' && !email.trim()) { setError('Enter an email.'); return }
    setLoading(true)
    try {
      const lead = await api.createLead(body)
      navigate(`/leads/${lead.id}`)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="h2">Create Lead</h1>
      <p className="caption" style={{ marginBottom: 24 }}>
        Pass either <strong>lead_id</strong> (tracking ID) or <strong>email</strong>, not both.
      </p>

      <div className="card" style={{ maxWidth: 480 }}>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <span className="label">Identifier: </span>
            <label style={{ marginRight: 16 }}>
              <input type="radio" name="mode" checked={mode === 'lead_id'} onChange={() => setMode('lead_id')} /> Lead ID (tracking_id)
            </label>
            <label>
              <input type="radio" name="mode" checked={mode === 'email'} onChange={() => setMode('email')} /> Email
            </label>
          </div>
          {mode === 'lead_id' && (
            <div className="form-group">
              <label>Lead ID (tracking_id) *</label>
              <input type="text" className="input" placeholder="e.g. t124" value={lead_id} onChange={(e) => setLeadId(e.target.value)} />
            </div>
          )}
          {mode === 'email' && (
            <div className="form-group">
              <label>Email *</label>
              <input type="email" className="input" placeholder="lead@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
          )}
          <div className="form-group">
            <label>Campaign name (optional)</label>
            <input type="text" className="input" placeholder="e.g. DubaiCamp" value={campaign_name} onChange={(e) => setCampaignName(e.target.value)} />
          </div>
          {error && <div className="alert alert-error">{error}</div>}
          <div style={{ display: 'flex', gap: 12 }}>
            <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Creating…' : 'Create lead'}</button>
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/')}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  )
}
