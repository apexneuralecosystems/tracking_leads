import { API_BASE_URL } from '../config'

/**
 * API client — see FRONTEND_CRM_CONNECTIVITY.md for base URL, auth (none), and lead shape.
 * GET/DELETE /leads/{lead_id} use the lead’s UUID id; tracking URLs use tracking_id.
 */

/**
 * Normalize API error detail (string or validation array) to a single message.
 * @param {string | Array<{ loc?: string[]; msg?: string }>} detail
 * @returns {string}
 */
function errorMessage(detail) {
  if (detail == null) return ''
  if (Array.isArray(detail)) return detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
  return String(detail)
}

async function request(path, options = {}) {
  const url = `${API_BASE_URL}${path}`
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
  if (res.status === 204) return null
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const msg = errorMessage(data.detail) || res.statusText || String(res.status)
    throw new Error(msg)
  }
  return data
}

/**
 * Build the tracking redirect URL: GET /go/{campaign_name}/{tracking_id}.
 * Use the lead’s tracking_id (e.g. "001"), not the lead’s UUID id.
 * @param {string} campaignName
 * @param {string} trackingId - Lead’s tracking_id (not lead.id).
 * @returns {string}
 */
export function getTrackingUrl(campaignName, trackingId) {
  const campaign = encodeURIComponent(campaignName || 'default')
  const tracking = encodeURIComponent(trackingId || '')
  return `${API_BASE_URL}/go/${campaign}/${tracking}`
}

export const api = {
  health: () => request('/health'),

  getLeads: (params = {}) => {
    const sp = new URLSearchParams()
    if (params.email) sp.set('email', params.email)
    if (params.tracking_id) sp.set('tracking_id', params.tracking_id)
    if (params.from_date) sp.set('from_date', params.from_date)
    if (params.to_date) sp.set('to_date', params.to_date)
    const q = sp.toString()
    return request(`/leads${q ? `?${q}` : ''}`)
  },

  getLead: (id) => request(`/leads/${id}`),

  createLead: (body) =>
    request('/leads', { method: 'POST', body: JSON.stringify(body) }),

  deleteLead: (id) => request(`/leads/${id}`, { method: 'DELETE' }),

  /** POST /events — event_type must be "open" or "click" */
  createEvent: (body) =>
    request('/events', { method: 'POST', body: JSON.stringify(body) }),
}
