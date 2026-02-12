"""
Tracking utilities: bot detection and client info extraction.

Bot filtering is necessary in B2B email campaigns because:
- Email providers (Gmail, Outlook) and security scanners often prefetch links.
- Social preview crawlers (Facebook, LinkedIn) hit links when emails are shared.
- Inflated click counts from bots skew conversion metrics and waste budget.
- Backend tracking is more reliable than email-tool tracking because we control
  the server, log the exact request (IP, UA, time), and can filter before storing.
"""

from __future__ import annotations

# Substrings that indicate bot/crawler traffic (case-insensitive)
BOT_UA_SUBSTRINGS = (
    "bot",
    "crawl",
    "spider",
    "preview",
    "facebookexternalhit",
)


def is_bot_user_agent(user_agent: str | None) -> bool:
    """Return True if the request appears to be from a bot/crawler."""
    if not user_agent or not user_agent.strip():
        return False
    ua_lower = user_agent.lower()
    return any(sub in ua_lower for sub in BOT_UA_SUBSTRINGS)


def get_client_ip(forwarded_for: str | None, remote_host: str | None) -> str | None:
    """
    Extract client IP handling X-Forwarded-For (first IP = client when behind proxy).
    """
    if forwarded_for:
        return forwarded_for.split(",")[0].strip() or None
    return remote_host
