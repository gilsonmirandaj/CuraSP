import json
import urllib.request
import urllib.error
from datetime import datetime
import re

DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]
VENUE_URL = 'https://shotgun.live/organizations/balaclava'

# Endpoints tentados em ordem até um responder com dados
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
    'Accept': 'application/json',
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


def _fetch_json(url: str):
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


def _extract_list(payload) -> list:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ('events', 'data', 'items', 'results'):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def get_balaclava_events():
    payload = None
    last_err = None

    for url in API_URLS:
        try:
            payload = _fetch_json(url)
            break
        except urllib.error.HTTPError as ex:
            last_err = ex
            if ex.code in (401, 403, 404):
                continue
            raise
        except Exception as ex:
            last_err = ex
            continue

    if payload is None:
        print(f'[balaclava] Todos os endpoints falharam. Último erro: {last_err}')
        return []

    raw = _extract_list(payload)
    if not raw:
        print('[balaclava] API retornou lista vazia ou formato desconhecido.')
        return []

    out = []
    for e in raw:
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

        # Tenta pegar nome do venue do evento (Shotgun inclui objeto venue)
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
