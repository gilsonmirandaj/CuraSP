import json
import urllib.request
from datetime import datetime
import re

DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]


def infer_genre(name: str) -> str:
    n = (name or '').lower()
    if re.search(r'rock|punk|metal|grunge', n): return 'Rock'
    if re.search(r'indie', n): return 'Indie Rock'
    if re.search(r'jazz', n): return 'Jazz'
    if re.search(r'samba|pagode', n): return 'Samba'
    if re.search(r'mpb|folk|acust', n): return 'MPB'
    if re.search(r'hip[ -]?hop|rap', n): return 'Hip-hop'
    if re.search(r'eletr|elet|\bdj\b|club|house|techno', n): return 'Eletrônica'
    if re.search(r'forr[oó]|baiao|baião', n): return 'Forró'
    return 'Indie Rock'


def get_picles_events():
    url = 'https://shotgun.live/api/organizations/picles/events?language=pt-br'
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
    with urllib.request.urlopen(req, timeout=20) as r:
        payload = json.loads(r.read().decode('utf-8'))
    events = payload.get('events', []) if isinstance(payload, dict) else []
    out = []
    for e in events:
        start = e.get('startDate') or e.get('start_at') or ''
        if not start:
            continue
        try:
            dt = datetime.fromisoformat(start.replace('Z', '+00:00')).astimezone()
        except Exception:
            continue
        slug = e.get('slug', '')
        out.append({
            'name': e.get('name', '').strip(),
            'detail': '',
            'date': f"{DAYS_PT[(dt.weekday() + 1) % 7]} {dt.day:02d}/{dt.month:02d}",
            'time': f"{dt.hour:02d}h{dt.minute:02d}" if dt.minute else f"{dt.hour:02d}h",
            'iso': dt.strftime('%Y-%m-%d'),
            'venue': 'Picles Cardeal',
            'v': 'picles',
            'genre': infer_genre(e.get('name', '')),
            'price': '',
            'url': f"https://shotgun.live/events/{slug}" if slug else 'https://shotgun.live/en/venues/picles'
        })
    return out
