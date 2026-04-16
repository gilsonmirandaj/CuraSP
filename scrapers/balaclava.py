import json
import re
import requests
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from datetime import datetime

DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]
VENUE_URL = 'https://shotgun.live/organizations/balaclava'

# Páginas HTML do Balaclava no Shotgun (Next.js embute __NEXT_DATA__)
PAGE_URLS = [
    'https://shotgun.live/organizations/balaclava',
    'https://shotgun.live/pt-br/organizations/balaclava',
]

# APIs REST — fallback
API_URLS = [
    'https://shotgun.live/api/organizations/balaclava/events?language=pt-br',
    'https://shotgun.live/api/v1/organizations/balaclava/events',
    'https://shotgun.live/api/v2/events?organization_slug=balaclava',
]

_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/json',
}


def infer_genre(name: str) -> str:
    n = (name or '').lower()
    if re.search(r'rock|punk|metal|grunge|hardcore', n): return 'Rock'
    if re.search(r'indie', n):                           return 'Indie Rock'
    if re.search(r'jazz', n):                            return 'Jazz'
    if re.search(r'pop', n):                             return 'Pop'
    if re.search(r'hip[ -]?hop|rap', n):                 return 'Hip-hop'
    if re.search(r'eletr|elet|\bdj\b|club|house|techno', n): return 'Eletrônica'
    return 'Indie/Pop'


def _parse_start(e: dict) -> str:
    for field in ('startDate', 'start_date', 'start_at', 'starts_at', 'startsAt', 'date'):
        val = e.get(field)
        if val:
            return str(val)
    return ''


def _find_events(obj, depth=0) -> list:
    """Busca recursiva por lista de eventos no JSON do __NEXT_DATA__."""
    if depth > 6:
        return []
    if isinstance(obj, list) and len(obj) > 0:
        first = obj[0]
        if isinstance(first, dict) and any(k in first for k in ('name', 'title', 'startDate', 'start_at', 'slug')):
            return obj
    if isinstance(obj, dict):
        for v in obj.values():
            result = _find_events(v, depth + 1)
            if result:
                return result
    return []


def _parse_raw_events(raw: list) -> list:
    out = []
    for e in raw:
        if not isinstance(e, dict):
            continue
        start = _parse_start(e)
        if not start:
            continue
        try:
            dt = datetime.fromisoformat(start.replace('Z', '+00:00')).astimezone()
        except Exception:
            continue

        name = (e.get('name') or e.get('title') or '').strip()
        if not name:
            continue

        slug = e.get('slug', '')
        venue_obj = e.get('venue') or {}
        venue_name = venue_obj.get('name', '') if isinstance(venue_obj, dict) else ''

        out.append({
            'name': name,
            'detail': '',
            'date': f"{DAYS_PT[(dt.weekday() + 1) % 7]} {dt.day:02d}/{dt.month:02d}",
            'time': f"{dt.hour:02d}h{dt.minute:02d}" if dt.minute else f"{dt.hour:02d}h",
            'iso': dt.strftime('%Y-%m-%d'),
            'venue': venue_name or 'Audio SP',
            'v': 'balaclava',
            'genre': infer_genre(name),
            'price': '',
            'url': f"https://shotgun.live/events/{slug}" if slug else VENUE_URL,
        })
    return out


def _scrape_next_data() -> list:
    """Extrai eventos do __NEXT_DATA__ embutido pelo Next.js do Shotgun."""
    for url in PAGE_URLS:
        try:
            res = requests.get(url, headers=_HEADERS, timeout=20)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            tag = soup.find('script', id='__NEXT_DATA__')
            if not tag or not tag.string:
                continue
            data = json.loads(tag.string)
            raw = _find_events(data)
            if raw:
                return _parse_raw_events(raw)
        except Exception:
            continue
    return []


def _scrape_api() -> list:
    for url in API_URLS:
        try:
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                payload = json.loads(r.read().decode('utf-8'))
            raw = payload if isinstance(payload, list) else payload.get('events', [])
            if raw:
                return _parse_raw_events(raw)
        except Exception:
            continue
    return []


def get_balaclava_events():
    events = _scrape_next_data()
    if events:
        return events
    events = _scrape_api()
    if events:
        return events
    print('[balaclava] Não foi possível coletar eventos.')
    return []
