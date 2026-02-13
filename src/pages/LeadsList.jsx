import { useState, useEffect } from 'react'
import { api } from '../api/client'
import { API_BASE_URL } from '../config'
import { formatDateIST } from '../utils/date'

export default function LeadsList() {
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deletingId, setDeletingId] = useState(null)
  const [filters, setFilters] = useState({
    email: '',
    tracking_id: '',
    from_date: '',
    to_date: '',
  })

  const fetchLeads = async () => {
    if (filters.from_date && filters.to_date && filters.from_date > filters.to_date) {
      setError('From date must be on or before to date.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const params = {}
      if (filters.email.trim()) params.email = filters.email.trim()
      if (filters.tracking_id.trim()) params.tracking_id = filters.tracking_id.trim()
      if (filters.from_date) params.from_date = filters.from_date
      if (filters.to_date) params.to_date = filters.to_date
      const data = await api.getLeads(params)
      setLeads(Array.isArray(data) ? data : [])
    } catch (e) {
      setError(e.message)
      setLeads([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLeads()
  }, [])

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this lead?')) return
    setDeletingId(id)
    setError(null)
    try {
      await api.deleteLead(id)
      setLeads((prev) => prev.filter((l) => l.id !== id))
    } catch (e) {
      setError(e.message)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div>
      <h1 className="h2">Leads</h1>

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 className="h4" style={{ marginBottom: 16 }}>Filters</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16 }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Email</label>
            <input
              type="text"
              className="input"
              placeholder="Filter by email"
              value={filters.email}
              onChange={(e) => handleFilterChange('email', e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Tracking ID</label>
            <input
              type="text"
              className="input"
              placeholder="Filter by tracking_id"
              value={filters.tracking_id}
              onChange={(e) => handleFilterChange('tracking_id', e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>From date</label>
            <input
              type="date"
              className="input"
              value={filters.from_date}
              onChange={(e) => handleFilterChange('from_date', e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>To date</label>
            <input
              type="date"
              className="input"
              value={filters.to_date}
              onChange={(e) => handleFilterChange('to_date', e.target.value)}
            />
          </div>
        </div>
        <div style={{ marginTop: 16 }}>
          <button type="button" className="btn btn-primary" onClick={fetchLeads}>
            Apply filters
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
          <p className="caption" style={{ marginTop: 8, marginBottom: 0 }}>
            Base URL: <code>{API_BASE_URL}</code>
          </p>
        </div>
      )}
      {loading && <p className="leads-loading">Loading leads…</p>}

      {!loading && !error && (
        <div className="card leads-results-card">
          <div className="leads-results-header">
            <h3 className="h4" style={{ margin: 0 }}>Results</h3>
            <span className="leads-results-count">{leads.length} lead{leads.length !== 1 ? 's' : ''}</span>
          </div>
          {leads.length === 0 ? (
            <div className="leads-empty">
              <p className="leads-empty-title">No leads found</p>
              <p className="caption">Try changing filters or create a new lead.</p>
            </div>
          ) : (
            <div className="table-wrap">
              <table className="leads-table">
                <caption className="table-caption">All times in Indian Standard Time (IST)</caption>
                <thead>
                  <tr>
                    <th>Tracking ID</th>
                    <th>Campaign name</th>
                    <th>Opened</th>
                    <th>First click at</th>
                    <th className="th-actions"></th>
                  </tr>
                </thead>
                <tbody>
                  {leads.map((lead) => (
                    <tr key={lead.id}>
                      <td><code className="cell-tracking-id">{lead.tracking_id}</code></td>
                      <td>{lead.campaign_name || '—'}</td>
                      <td><span className="status-opened">Opened</span></td>
                      <td className="cell-date">{formatDateIST(lead.first_click_at)}</td>
                      <td className="cell-actions">
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(lead.id)}
                          disabled={deletingId === lead.id}
                        >
                          {deletingId === lead.id ? '…' : 'Delete'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
