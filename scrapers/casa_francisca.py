import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

URL = 'https://site.bileto.sympla.com.br/casadefrancisca/'
MONTHS = {'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12}
DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]


def normalize_url(url: str) -> str:
    if not url:
        return URL
    if url.startswith('/'):
        return 'https://site.bileto.sympla.com.br' + url
    return url


def parse_iso(text: str) -> str:
    t = ' '.join((text or '').split()).lower()
    m = re.search(r'(\d{1,2})\s+de\s+([a-zç]{3,})', t)
    if not m:
        return ''
    day = int(m.group(1))
    mon_txt = m.group(2)[:3]
    month = MONTHS.get(mon_txt)
    if not month:
        return ''
    year = datetime.now().year
    try:
        return datetime(year, month, day).strftime('%Y-%m-%d')
    except Exception:
        return ''


def fmt_date(iso: str) -> str:
    if not iso:
        return '2026'
    dt = datetime.fromisoformat(iso)
    return f"{DAYS_PT[(dt.weekday() + 1) % 7]} {dt.day:02d}/{dt.month:02d}"


def get_casa_francisca_events():
    res = requests.get(URL, timeout=20, headers={'User-Agent':'Mozilla/5.0'})
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    events = []
    seen = set()
    for a in soup.select('a[href]'):
        href = normalize_url(a.get('href', ''))
        text = ' '.join(a.get_text(' ', strip=True).split())
        if not text or len(text) < 6:
            continue
        if 'casadefrancisca' not in href and 'sympla' not in href:
            continue
        iso = parse_iso(text)
        name = re.sub(r'\s+', ' ', text)
        key = (name.lower(), href)
        if key in seen:
            continue
        seen.add(key)
        events.append({
            'name': name[:140],
            'detail': 'Programação oficial da Casa de Francisca',
            'date': fmt_date(iso),
            'time': '',
            'iso': iso,
            'venue': 'Casa de Francisca',
            'v': 'francisca',
            'genre': 'MPB / Samba / Jazz / Brasilidades',
            'price': '',
            'url': href
        })
    if not events:
        events.append({
            'name': 'Casa de Francisca — programação oficial',
            'detail': 'Consulte a agenda atual da casa na página oficial da Sympla',
            'date': '2026',
            'time': '',
            'iso': '',
            'venue': 'Casa de Francisca',
            'v': 'francisca',
            'genre': 'MPB / Samba / Jazz / Brasilidades',
            'price': '',
            'url': URL
        })
    return events
