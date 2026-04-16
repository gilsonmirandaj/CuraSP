import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from datetime import datetime
import re

# Tenta múltiplas URLs da Bona em ordem
CANDIDATE_URLS = [
    'https://bonacasademusica.com.br/agenda',
    'https://bonacasademusica.com.br/programacao',
    'https://bonacasademusica.com.br',
]
BASE_URL = 'https://bonacasademusica.com.br'

DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]
MONTHS = {
    'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,
    'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12,
}

# Domínios aceitos como links de evento
_TICKET_DOMAINS = ('bonacasademusica', 'eventim.com.br', 'sympla.com.br', 'ingresse.com', 'bileto')


def parse_iso(text: str) -> str:
    t = ' '.join((text or '').split()).lower()
    m = re.search(r'(\d{1,2})\s+(?:de\s+)?([a-zç]{3,})', t)
    if m:
        day = int(m.group(1))
        month = MONTHS.get(m.group(2)[:3])
        if month:
            now = datetime.now()
            year = now.year
            try:
                dt = datetime(year, month, day)
                if dt.date() < now.date() and month < now.month:
                    dt = datetime(year + 1, month, day)
                return dt.strftime('%Y-%m-%d')
            except Exception:
                pass
    m2 = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{4}))?', t)
    if m2:
        day, month = int(m2.group(1)), int(m2.group(2))
        year = int(m2.group(3)) if m2.group(3) else datetime.now().year
        try:
            return datetime(year, month, day).strftime('%Y-%m-%d')
        except Exception:
            pass
    return ''


def fmt_date(iso: str) -> str:
    if not iso:
        return ''
    dt = datetime.fromisoformat(iso)
    return f"{DAYS_PT[(dt.weekday() + 1) % 7]} {dt.day:02d}/{dt.month:02d}"


def _build_events(soup: BeautifulSoup, page_url: str) -> list:
    events = []
    seen = set()
    for a in soup.select('a[href]'):
        href = (a.get('href') or '').strip()
        if not href:
            continue
        if href.startswith('/'):
            href = BASE_URL + href
        if not any(d in href for d in _TICKET_DOMAINS):
            continue
        # Descarta link genérico da home
        if href.rstrip('/') in (BASE_URL, BASE_URL + '/agenda', BASE_URL + '/programacao'):
            continue
        raw = ' '.join(a.get_text('\n', strip=True).split())
        if len(raw) < 4:
            continue
        iso = parse_iso(raw)
        lines = [l.strip() for l in a.get_text('\n', strip=True).split('\n') if l.strip()]
        name = re.sub(r'\s+', ' ', lines[0] if lines else raw)[:140]
        key = (name.lower(), href)
        if key in seen:
            continue
        seen.add(key)
        events.append({
            'name': name,
            'detail': 'Programação da Bona Casa de Música',
            'date': fmt_date(iso),
            'time': '',
            'iso': iso,
            'venue': 'Bona Casa de Música',
            'v': 'bona',
            'genre': 'MPB / Folk / Jazz',
            'price': '',
            'url': href,
        })
    return events


def get_bona_events():
    # Tenta requests + BeautifulSoup em cada URL candidata
    for url in CANDIDATE_URLS:
        try:
            res = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            events = _build_events(soup, url)
            if events:
                return events
        except Exception:
            continue

    # Fallback: Playwright para páginas JS-rendered
    try:
        return _scrape_playwright()
    except Exception as ex:
        print(f'[bona] Falhou: {ex}')
        return []


def _scrape_playwright():
    for url in CANDIDATE_URLS:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
                page = browser.new_page(
                    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                try:
                    page.goto(url, wait_until='networkidle', timeout=25000)
                except Exception:
                    page.goto(url, wait_until='domcontentloaded', timeout=25000)
                page.wait_for_timeout(2000)
                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, 'html.parser')
            events = _build_events(soup, url)
            if events:
                return events
        except Exception:
            continue
    return []
