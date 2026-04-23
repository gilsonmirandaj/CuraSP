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
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'pt-BR,pt;q=0.9',
}


def parse_iso(text: str) -> str:
    t = ' '.join((text or '').split()).lower()
    m = re.search(r'(\d{1,2})\s+de\s+([a-zç]{3,})', t)
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
    return f"{DAYS_PT[(dt.weekday() + 1) % 7]} {dt.day:02d}/{dt.month:02d}"


def normalize_href(href: str) -> str:
    if not href:
        return URL
    if href.startswith('//'):
        return 'https:' + href
    if href.startswith('/'):
        return 'https://site.bileto.sympla.com.br' + href
    return href


def _find_events_json(obj, depth=0) -> list:
    if depth > 6:
        return []
    if isinstance(obj, list) and len(obj) > 0:
        first = obj[0]
        if isinstance(first, dict) and any(k in first for k in ('name','title','startDate','start_at','slug','id')):
            return obj
    if isinstance(obj, dict):
        for v in obj.values():
            r = _find_events_json(v, depth + 1)
            if r:
                return r
    return []


def _events_from_next_data(data: dict) -> list:
    events, seen = [], set()
    for e in _find_events_json(data):
        if not isinstance(e, dict):
            continue
        name = (e.get('name') or e.get('title') or '').strip()
        if not name or len(name) < 4:
            continue
        href = normalize_href(e.get('url') or e.get('link') or '')
        start = e.get('startDate') or e.get('start_date') or e.get('start_at') or ''
        iso = ''
        if start:
            try:
                from datetime import timezone
                dt = datetime.fromisoformat(str(start).replace('Z', '+00:00'))
                iso = dt.strftime('%Y-%m-%d')
            except Exception:
                iso = parse_iso(str(start))
        key = (name.lower(), href)
        if key in seen:
            continue
        seen.add(key)
        events.append(_make_event(name, iso, href))
    return events


def _events_from_links(soup: BeautifulSoup) -> list:
    events, seen = [], set()
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
        events.append(_make_event(name, iso, href))
    return events


def _make_event(name: str, iso: str, href: str) -> dict:
    return {
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
    }


def get_casa_francisca_events():
    # Tentativa 1: requests (SSR ou __NEXT_DATA__)
    try:
        res = requests.get(URL, headers=_HEADERS, timeout=20)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        print(f'[francisca] requests OK — {len(res.text)} bytes')

        tag = soup.find('script', id='__NEXT_DATA__')
        if tag and tag.string:
            events = _events_from_next_data(json.loads(tag.string))
            if events:
                print(f'[francisca] {len(events)} eventos via __NEXT_DATA__')
                return events

        events = _events_from_links(soup)
        if events:
            print(f'[francisca] {len(events)} eventos via links HTML')
            return events

        print('[francisca] requests OK mas nenhum evento encontrado no HTML')
    except Exception as ex:
        print(f'[francisca] requests falhou: {ex}')

    # Tentativa 2: Playwright com stealth
    try:
        return _scrape_playwright()
    except Exception as ex:
        print(f'[francisca] Playwright falhou: {ex}')
        return []


def _scrape_playwright():
    from playwright.sync_api import sync_playwright
    from scrapers._browser import stealth_page, goto_safe

    with sync_playwright() as p:
        browser, ctx, page = stealth_page(p)
        try:
            goto_safe(page, URL)
            page.wait_for_timeout(4000)
            print(f'[francisca] Playwright carregou — title: {page.title()!r}')

            # Tenta __NEXT_DATA__ via JS
            try:
                nd = page.evaluate('() => { const s = document.getElementById("__NEXT_DATA__"); return s ? s.textContent : null; }')
                if nd:
                    events = _events_from_next_data(json.loads(nd))
                    if events:
                        print(f'[francisca] {len(events)} eventos via __NEXT_DATA__ (Playwright)')
                        return events
            except Exception:
                pass

            anchors = page.eval_on_selector_all('a[href]', '''els => els.map(el => ({
                href: el.href || "",
                text: el.innerText || "",
            }))''')
        finally:
            ctx.close()
            browser.close()

    seen, events = set(), []
    for a in anchors:
        href = normalize_href(a.get('href', ''))
        if not any(k in href for k in ('sympla.com.br', 'bileto.sympla', 'casadefrancisca')):
            continue
        if href.rstrip('/') in {URL.rstrip('/'), 'https://sympla.com.br'}:
            continue
        raw = ' '.join((a.get('text') or '').split())
        if len(raw) < 4:
            continue
        iso = parse_iso(raw)
        lines = [l.strip() for l in (a.get('text') or '').split('\n') if l.strip()]
        name = re.sub(r'\s+', ' ', lines[0] if lines else raw)[:140]
        key = (name.lower(), href)
        if key in seen:
            continue
        seen.add(key)
        events.append(_make_event(name, iso, href))

    print(f'[francisca] {len(events)} eventos via Playwright DOM')
    return events
