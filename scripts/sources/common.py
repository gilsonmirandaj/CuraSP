from __future__ import annotations
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urljoin

DAYS_PT = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]
TZ = ZoneInfo("America/Sao_Paulo")


def infer_genre(name: str) -> str:
    n = (name or "").lower()
    if re.search(r'rock|punk|metal|grunge|post-punk', n): return "Rock"
    if re.search(r'indie', n): return "Indie Rock"
    if re.search(r'jazz|choro', n): return "Jazz"
    if re.search(r'samba|pagode', n): return "Samba"
    if re.search(r'mpb|folk|acustic|canção|cantam', n): return "MPB"
    if re.search(r'hip.hop|rap|trap|grime', n): return "Hip-hop"
    if re.search(r'eletr|elet|\bdj\b|club|house|techno', n): return "Eletronica"
    if re.search(r'forro|baiao', n): return "Forro"
    if re.search(r'reggae|dub', n): return "Reggae"
    return "Indie Rock"


def format_date_parts(dt: datetime) -> tuple[str, str, str]:
    dt_local = dt.astimezone(TZ)
    wd = (dt_local.weekday() + 1) % 7
    date_str = f"{DAYS_PT[wd]} {dt_local.day:02d}/{dt_local.month:02d}"
    time_str = f"{dt_local.hour:02d}h{dt_local.minute:02d}" if dt_local.minute else f"{dt_local.hour:02d}h"
    iso_str = dt_local.strftime('%Y-%m-%d')
    return date_str, time_str, iso_str


def normalize_event(*, name, detail='', date='', time='', iso='', venue='', v='', genre='', price='', url=''):
    return {
        'name': (name or '').strip(),
        'detail': (detail or '').strip(),
        'date': (date or '').strip(),
        'time': (time or '').strip(),
        'iso': (iso or '').strip(),
        'venue': (venue or '').strip(),
        'v': (v or '').strip(),
        'genre': (genre or infer_genre(name or '')).strip(),
        'price': (price or '').strip(),
        'url': (url or '').strip(),
    }


def url_abs(base: str, href: str | None) -> str:
    return urljoin(base, href or '')


def dedupe_events(events):
    seen = set()
    out = []
    for e in events:
        key = f"{(e.get('name') or '').lower()}|{e.get('iso') or ''}|{e.get('v') or ''}|{e.get('venue') or ''}"
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


def sort_events(events):
    return sorted(events, key=lambda e: (e.get('iso') or '9999-99-99', e.get('time') or '99h99', e.get('name') or ''))
