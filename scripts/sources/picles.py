from __future__ import annotations
import json, urllib.request
from datetime import datetime
from .common import format_date_parts, normalize_event, infer_genre

URL = "https://shotgun.live/api/organizations/picles/events?language=pt-br"


def fetch_events():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())
    result = []
    for e in data.get('events', []):
        start = e.get('startDate')
        if not start:
            continue
        dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        date_str, time_str, iso_str = format_date_parts(dt)
        slug = e.get('slug', '')
        result.append(normalize_event(
            name=e.get('name', ''), detail='', date=date_str, time=time_str, iso=iso_str,
            venue='Picles Cardeal', v='picles', genre=infer_genre(e.get('name', '')), price='',
            url=f"https://shotgun.live/events/{slug}" if slug else 'https://shotgun.live/en/venues/picles'
        ))
    return result
