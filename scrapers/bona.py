import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

CANDIDATE_URLS = [
    'https://www.bonacasademusica.com.br/agenda',
    'https://www.bonacasademusica.com.br/programacao',
    'https://www.bonacasademusica.com.br',
    'https://bonacasademusica.com.br/agenda',
    'https://bonacasademusica.com.br',
]
BASE_DOMAIN = 'bonacasademusica.com.br'
EVENTIM_URL = 'https://www.eventim.com.br/artist/bona-casa-musica/'

DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]
MONTHS = {'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12}

_TICKET_DOMAINS = ('bonacasademusica', 'eventim.com.br', 'sympla.com.br', 'ingresse.com', 'bileto')

_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'pt-BR,pt;q=0.9',
}


def parse_iso(text: str) -> str:
    t = ' '.join((text or '').split()).lower()
    m = re.search(r'(\d{1,2})\s+(?:de\s+)?([a-zç]{3,})', t)
    if m:
        day, month = int(m.group(1)), MONTHS.get(m.group(2)[:3])
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
    return f"{DAYS_PT[(dt.weekday()+1)%7]} {dt.day:02d}/{dt.month:02d}"


def _build_events(soup: BeautifulSoup, page_url: str) -> list:
    events, seen = [], set()
    for a in soup.select('a[href]'):
        href = (a.get('href') or '').strip()
        if not href:
            continue
        if href.startswith('/'):
            from urllib.parse import urljoin
            href = urljoin(page_url, href)
        if not any(d in href for d in _TICKET_DOMAINS):
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
    # Tentativa 1: requests em cada URL candidata
    for url in CANDIDATE_URLS:
        try:
            res = requests.get(url, headers=_HEADERS, timeout=15, allow_redirects=True)
            res.raise_for_status()
            print(f'[bona] requests OK ({url}) — {res.status_code}, {len(res.text)} bytes')
            soup = BeautifulSoup(res.text, 'html.parser')
            events = _build_events(soup, url)
            if events:
                print(f'[bona] {len(events)} eventos via requests')
                return events
            print(f'[bona] {url} OK mas sem eventos no HTML')
        except Exception as ex:
            print(f'[bona] requests falhou ({url}): {ex}')

    # Tentativa 2: Playwright com stealth
    try:
        return _scrape_playwright()
    except Exception as ex:
        print(f'[bona] Playwright falhou: {ex}')
        return []


def _scrape_playwright():
    from playwright.sync_api import sync_playwright
    from scrapers._browser import stealth_page, goto_safe

    for url in CANDIDATE_URLS:
        try:
            with sync_playwright() as p:
                browser, ctx, page = stealth_page(p)
                try:
                    goto_safe(page, url, timeout=25000)
                    page.wait_for_timeout(3000)
                    print(f'[bona] Playwright ({url}) — title: {page.title()!r}')
                    html = page.content()
                finally:
                    ctx.close()
                    browser.close()

            soup = BeautifulSoup(html, 'html.parser')
            events = _build_events(soup, url)
            if events:
                print(f'[bona] {len(events)} eventos via Playwright')
                return events
        except Exception as ex:
            print(f'[bona] Playwright falhou ({url}): {ex}')

    return []
