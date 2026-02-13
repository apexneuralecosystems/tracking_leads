#!/usr/bin/env bash
# Test all APIs with curl. Creates example leads and verifies endpoints.
# Usage: API_BASE_URL=https://api.meetapexneural.com ./scripts/test_api.sh
# Or:   ./scripts/test_api.sh   (uses default below)

set -e
BASE_URL="${API_BASE_URL:-https://api.meetapexneural.com}"
echo "=== Base URL: $BASE_URL ==="

# --- 1. Health ---
echo ""
echo "--- 1. GET /health ---"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/health"
echo ""

# --- 2. Create example leads (POST /leads) ---
echo "--- 2. POST /leads (create example leads) ---"

echo "Create lead with lead_id only (tracking_id=ex-lead-dubai-001)..."
L1=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/leads" \
  -H "Content-Type: application/json" \
  -d '{"lead_id":"ex-lead-dubai-001","campaign_name":"DubaiCamp"}')
HTTP_L1=$(echo "$L1" | tail -n1)
BODY_L1=$(echo "$L1" | sed '$d')
echo "$BODY_L1" | head -c 200
echo "... [HTTP $HTTP_L1]"

echo "Create lead with email only..."
L2=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/leads" \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","campaign_name":"Webinar2025"}')
HTTP_L2=$(echo "$L2" | tail -n1)
BODY_L2=$(echo "$L2" | sed '$d')
echo "$BODY_L2" | head -c 200
echo "... [HTTP $HTTP_L2]"

echo "Create lead with email (second example)..."
L3=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/leads" \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","campaign_name":"Newsletter"}')
HTTP_L3=$(echo "$L3" | tail -n1)
BODY_L3=$(echo "$L3" | sed '$d')
echo "$BODY_L3" | head -c 200
echo "... [HTTP $HTTP_L3]"

# Extract first lead UUID for get/delete (if jq available)
if command -v jq &>/dev/null; then
  LEAD_UUID=$(echo "$BODY_L1" | jq -r '.id')
  echo "First lead id: $LEAD_UUID"
else
  echo "(Install jq to run get-by-id and delete tests with parsed id)"
  LEAD_UUID=""
fi

# --- 3. List all leads ---
echo ""
echo "--- 3. GET /leads (list all) ---"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/leads"
echo ""

# --- 4. List with filters ---
echo "--- 4. GET /leads?email=alice@example.com ---"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/leads?email=alice@example.com"
echo ""

echo "--- 5. GET /leads?tracking_id=ex-lead-dubai-001 ---"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/leads?tracking_id=ex-lead-dubai-001"
echo ""

echo "--- 6. GET /leads?from_date=2025-01-01&to_date=2025-12-31 ---"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/leads?from_date=2025-01-01&to_date=2025-12-31"
echo ""

# --- 7. Get lead by ID ---
if [ -n "$LEAD_UUID" ] && [ "$LEAD_UUID" != "null" ]; then
  echo "--- 7. GET /leads/$LEAD_UUID ---"
  curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/leads/$LEAD_UUID"
  echo ""
fi

# --- 8. POST /events ---
echo "--- 8. POST /events (open) ---"
curl -s -w "\nHTTP %{http_code}\n" -X POST "$BASE_URL/events" \
  -H "Content-Type: application/json" \
  -d '{"tracking_id":"ex-lead-dubai-001","event_type":"open"}'
echo ""

echo "--- 9. POST /events (click) ---"
curl -s -w "\nHTTP %{http_code}\n" -X POST "$BASE_URL/events" \
  -H "Content-Type: application/json" \
  -d '{"tracking_id":"ex-lead-dubai-001","event_type":"click"}'
echo ""

# --- 10. GET /go (tracking redirect) ---
echo "--- 10. GET /go/DubaiCamp/ex-lead-dubai-001 (expect 302 redirect) ---"
curl -s -I "$BASE_URL/go/DubaiCamp/ex-lead-dubai-001" 2>/dev/null | head -5
echo ""

# --- 11. Delete one lead ---
if [ -n "$LEAD_UUID" ] && [ "$LEAD_UUID" != "null" ]; then
  echo "--- 11. DELETE /leads/$LEAD_UUID ---"
  curl -s -w "HTTP %{http_code}\n" -X DELETE "$BASE_URL/leads/$LEAD_UUID"
  echo ""
fi

# --- 12. List again (one less) ---
echo "--- 12. GET /leads (after delete) ---"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/leads"
echo ""

echo "=== Done. Check HTTP codes: health 200, create 201, list/get 200, delete 204, redirect 302. ==="
