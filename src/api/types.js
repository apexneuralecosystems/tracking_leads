/**
 * API types — matches https://api.meetapexneural.com (see FRONTEND_CRM_CONNECTIVITY.md).
 * No first_name or company; lead shape is id, tracking_id, campaign_name, email,
 * created_at, opened_at, first_click_at. Use lead.tracking_id (not lead.id) in tracking URLs.
 *
 * @typedef {Object} Lead
 * @property {string} id - UUID; use for GET/DELETE by id.
 * @property {string} tracking_id - Short id; use in /go and filters.
 * @property {string|null} campaign_name
 * @property {string} email - Can be "" if lead created with only lead_id.
 * @property {string} created_at - ISO 8601 UTC.
 * @property {string|null} opened_at - When they first opened (e.g. email); set by POST /events event_type "open".
 * @property {string|null} first_click_at - When they first hit GET /go (tracking link).
 *
 * @typedef {Object} LeadCreate
 * @property {string} [lead_id] - Tracking ID. Use lead_id OR email.
 * @property {string} [email] - Use lead_id OR email.
 * @property {string|null} [campaign_name] - Optional.
 *
 * @typedef {Object} EventCreate
 * @property {string} tracking_id - Must match a lead’s tracking_id.
 * @property {'open'|'click'} event_type
 *
 * @typedef {Object} Event
 * @property {string} id
 * @property {string} tracking_id
 * @property {'open'|'click'} event_type
 * @property {string} created_at
 *
 * @typedef {Object} ApiError
 * @property {string | Array<{ loc: string[]; msg: string; type?: string }>} detail
 */

export default {}
