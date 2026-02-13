/** Indian Standard Time (Asia/Kolkata). Use for opened_at, first_click_at, etc. */

const IST_OPTIONS = { timeZone: 'Asia/Kolkata', dateStyle: 'short', timeStyle: 'short' }

/**
 * Format an ISO 8601 date string for display in Indian time.
 * @param {string|null|undefined} iso
 * @returns {string} Formatted string or "—" if empty
 */
export function formatDateIST(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString('en-IN', IST_OPTIONS)
}
