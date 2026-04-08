from __future__ import annotations
from fallback.static_events import FALLBACK_BY_SOURCE

def fetch_events():
    return FALLBACK_BY_SOURCE.get('sesc', [])
