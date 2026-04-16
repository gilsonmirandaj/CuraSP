import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = 'https://site.bileto.sympla.com.br/casadefrancisca/'
MONTHS = {'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12}
DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]

_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/json',
}


def parse_iso(text: str) -> str:
    t = ' '.join((text or '').split()).lower()

    m = re.search(r'(\d{1,2})\s+de\s+([a-zç]{3,})', t)
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


def normalize_href(href: str) -> str:
    if not href:
        return URL
    if href.startswith('//'):
        return 'https:' + href
    if href.startswith('/'):
        return 'https://site.bileto.sympla.com.br' + href
    return href


def _find_events(obj, depth=0) -> list:
    """Busca recursiva por lista de eventos dentro do __NEXT_DATA__ JSON."""
    if depth > 6:
        return []
    if isinstance(obj, list) and len(obj) > 0:
        first = obj[0]
        if isinstance(first, dict) and any(k in first for k in ('name', 'title', 'startDate', 'start_date', 'slug', 'id')):
            return obj
    if isinstance(obj, dict):
        for v in obj.values():
            result = _find_events(v, depth + 1)
            if result:
                return result
    return []


def _parse_next_data(data: dict) -> list:
    events = []
    seen = set()
    raw = _find_events(data)
    for e in raw:
        if not isinstance(e, dict):
            continue
        name = (e.get('name') or e.get('title') or '').strip()
        if not name or len(name) < 4:
            continue

        # Tenta extrair URL do evento
        href = normalize_href(e.get('url') or e.get('link') or e.get('slug') or '')
        if e.get('slug') and not href.startswith('http'):
            href = 'https://site.bileto.sympla.com.br/casadefrancisca/' + e.get('slug', '')

        # Tenta extrair data
        start = e.get('startDate') or e.get('start_date') or e.get('start_at') or e.get('date') or ''
        iso = ''
        if start:
            try:
                dt = datetime.fromisoformat(str(start).replace('Z', '+00:00')).astimezone()
                iso = dt.strftime('%Y-%m-%d')
            except Exception:
                iso = parse_iso(str(start))
        if not iso:
            iso = parse_iso(name)

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
            'url': href or URL,
        })
    return events


def _parse_links(soup: BeautifulSoup) -> list:
    """Extrai eventos a partir de <a href> visíveis na página (SSR ou estático)."""
    events = []
    seen = set()
    for a in soup.select('a[href]'):
        href = normalize_href(a.get('href', ''))
        if not any(k in href for k in ('sympla.com.br', 'bileto.sympla', 'casadefrancisca')):
            continue
        if href.rstrip('/') in {URL.rstrip('/'), 'https://sympla.com.br', 'https://www.sympla.com.br'}:
            continue
        raw = ' '.join(a.get_text(' ', strip=True).split())
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
            'detail': 'Programação oficial da Casa de Francisca',
            'date': fmt_date(iso),
            'time': '',
            'iso': iso,
            'venue': 'Casa de Francisca',
            'v': 'francisca',
            'genre': 'MPB / Samba / Jazz / Brasilidades',
            'price': '',
            'url': href,
        })
    return events


def get_casa_francisca_events():
    try:
        res = requests.get(URL, headers=_HEADERS, timeout=20)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        # Estratégia 1: __NEXT_DATA__ (Bileto usa React/Next.js)
        tag = soup.find('script', id='__NEXT_DATA__')
        if tag and tag.string:
            data = json.loads(tag.string)
            events = _parse_next_data(data)
            if events:
                return events

        # Estratégia 2: links <a href> renderizados no HTML
        events = _parse_links(soup)
        if events:
            return events

    except Exception as ex:
        print(f'[casa_francisca] requests falhou: {ex}')

    # Estratégia 3: Playwright (para quando rodar no GitHub Actions)
    try:
        return _scrape_playwright()
    except Exception as ex:
        print(f'[casa_francisca] Playwright falhou: {ex}')
        return []


def _scrape_playwright():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page(user_agent=_HEADERS['User-Agent'])
        try:
            page.goto(URL, wait_until='networkidle', timeout=30000)
        except Exception:
            page.goto(URL, wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(3000)

        # Tenta __NEXT_DATA__ via JS
        try:
            next_data = page.evaluate('() => { const el = document.getElementById("__NEXT_DATA__"); return el ? el.textContent : null; }')
            if next_data:
                data = json.loads(next_data)
                events = _parse_next_data(data)
                if events:
                    browser.close()
                    return events
        except Exception:
            pass

        anchors = page.eval_on_selector_all('a[href]', '''els => els.map(el => ({
            href: el.href || "",
            text: el.innerText || "",
            title: el.getAttribute("title") || ""
        }))''')
        browser.close()

    seen = set()
    events = []
    for a in anchors:
        href = normalize_href(a.get('href', ''))
        if not any(k in href for k in ('sympla.com.br', 'bileto.sympla', 'casadefrancisca')):
            continue
        if href.rstrip('/') in {URL.rstrip('/'), 'https://sympla.com.br'}:
            continue
        raw = ' '.join((a.get('text') or a.get('title') or '').split())
        if len(raw) < 4:
            continue
        iso = parse_iso(raw)
        lines = [l.strip() for l in (a.get('text') or '').split('\n') if l.strip()]
        name = re.sub(r'\s+', ' ', lines[0] if lines else raw)[:140]
        key = (name.lower(), href)
        if key in seen:
            continue
        seen.add(key)
        events.append({
            'name': name,
            'detail': 'Programação oficial da Casa de Francisca',
            'date': fmt_date(iso),
            'time': '',
            'iso': iso,
            'venue': 'Casa de Francisca',
            'v': 'francisca',
            'genre': 'MPB / Samba / Jazz / Brasilidades',
            'price': '',
            'url': href,
        })
    return events
