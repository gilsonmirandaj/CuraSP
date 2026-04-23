import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = 'https://meaple.com.br/rockambole'
DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]
MONTHS = {'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12}

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


def _build_events(anchors: list) -> list:
    events, seen = [], set()
    for a in anchors:
        href = (a.get('href') or '').strip()
        if not href or 'meaple.com.br' not in href:
            continue
        if href.rstrip('/') == URL.rstrip('/'):
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
            'detail': '',
            'date': fmt_date(iso),
            'time': '',
            'iso': iso,
            'venue': 'Casa Rockambole',
            'v': 'rockambole',
            'genre': 'Experimental / Rock / Noise',
            'price': '',
            'url': href,
        })
    return events


def get_casa_rockambole_events():
    # Tentativa 1: requests
    try:
        res = requests.get(URL, headers=_HEADERS, timeout=15)
        res.raise_for_status()
        print(f'[rockambole] requests OK — {res.status_code}, {len(res.text)} bytes')
        soup = BeautifulSoup(res.text, 'html.parser')
        anchors = [
            {'href': a.get('href', ''), 'text': a.get_text('\n', strip=True), 'title': a.get('title', '')}
            for a in soup.select('a[href]')
        ]
        events = _build_events(anchors)
        if events:
            print(f'[rockambole] {len(events)} eventos via requests')
            return events
        print('[rockambole] requests OK mas nenhum evento encontrado')
    except Exception as ex:
        print(f'[rockambole] requests falhou: {ex}')

    # Tentativa 2: Playwright com stealth
    try:
        return _scrape_playwright()
    except Exception as ex:
        print(f'[rockambole] Playwright falhou: {ex}')
        return []


def _scrape_playwright():
    from playwright.sync_api import sync_playwright
    from scrapers._browser import stealth_page, goto_safe

    with sync_playwright() as p:
        browser, ctx, page = stealth_page(p)
        try:
            goto_safe(page, URL)
            page.wait_for_timeout(4000)
            print(f'[rockambole] Playwright — title: {page.title()!r}')
            anchors = page.eval_on_selector_all('a[href]', '''els => els.map(el => ({
                href: el.href || "",
                text: el.innerText || "",
                title: el.getAttribute("title") || ""
            }))''')
        finally:
            ctx.close()
            browser.close()

    events = _build_events(anchors)
    print(f'[rockambole] {len(events)} eventos via Playwright')
    return events
