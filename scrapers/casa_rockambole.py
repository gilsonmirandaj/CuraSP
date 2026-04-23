import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = 'https://meaple.com.br/rockambole'
DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]
MONTHS = {
    'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,
    'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12,
}

_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Meaple JavaScript to extract structured event cards from the DOM
_EXTRACT_JS = '''() => {
    const results = [];
    const seen = new Set();

    // Strategy 1: look for cards that have a meaple link + a heading
    const cardSels = [
        '[class*="event"]', '[class*="Event"]',
        '[class*="card"]',  '[class*="Card"]',
        '[class*="ingresso"]', '[class*="Ingresso"]',
        'article', 'li',
    ];
    for (const sel of cardSels) {
        const eventRe = /meaple\.com\.br\/rockambole\/.+/;
        const cards = [...document.querySelectorAll(sel)].filter(el => {
            const link = el.querySelector('a[href*="meaple.com.br/rockambole/"]') || (el.tagName==='A' && eventRe.test(el.href) ? el : null);
            return link && el.innerText && el.innerText.trim().length > 5;
        });
        if (cards.length === 0) continue;
        for (const card of cards) {
            const linkEl = card.querySelector('a[href*="meaple.com.br/rockambole/"]') || (card.tagName==='A' ? card : null);
            const href = linkEl?.href || '';
            if (!href || !eventRe.test(href)) continue;
            if (seen.has(href)) continue;
            seen.add(href);
            const heading = card.querySelector('h1,h2,h3,h4,h5,[class*="title"],[class*="Title"],[class*="nome"],[class*="Name"]');
            const dateEl  = card.querySelector('time,[class*="date"],[class*="Date"],[class*="data"],[class*="Data"],[class*="quando"]');
            const timeEl  = card.querySelector('[class*="hour"],[class*="hora"],[class*="time"],[class*="Time"]');
            const priceEl = card.querySelector('[class*="price"],[class*="Price"],[class*="prec"],[class*="valor"],[class*="Valor"],[class*="ingress"]');
            results.push({
                href,
                name:  heading?.innerText?.trim()  || '',
                date:  dateEl?.getAttribute('datetime') || dateEl?.innerText?.trim()  || '',
                time:  timeEl?.innerText?.trim()   || '',
                price: priceEl?.innerText?.trim()  || '',
                text:  card.innerText?.trim()      || '',
            });
        }
        if (results.length) break;
    }

    // Strategy 2: all rockambole event links if cards gave nothing
    if (!results.length) {
        const eventPattern = /meaple\.com\.br\/rockambole\/.+/;
        for (const el of document.querySelectorAll('a[href*="meaple.com.br/rockambole/"]')) {
            const href = el.href;
            if (!href || !eventPattern.test(href)) continue;
            if (seen.has(href)) continue;
            seen.add(href);
            results.push({ href, name: '', date: '', time: '', price: '', text: el.innerText?.trim() || '' });
        }
    }
    return results;
}'''


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


def _find_events_json(obj, depth=0) -> list:
    """Recursively find an event list in a parsed JSON object."""
    if depth > 8:
        return []
    if isinstance(obj, list) and len(obj) > 0:
        first = obj[0]
        if isinstance(first, dict) and any(k in first for k in
                ('name', 'title', 'slug', 'startDate', 'start_at', 'starts_at', 'startsAt')):
            return obj
    if isinstance(obj, dict):
        for v in obj.values():
            r = _find_events_json(v, depth + 1)
            if r:
                return r
    return []


def _parse_json_events(raw: list) -> list:
    out = []
    for e in raw:
        if not isinstance(e, dict):
            continue
        name = (e.get('name') or e.get('title') or '').strip()
        if not name:
            continue
        slug = e.get('slug') or e.get('url') or ''
        url = f'https://meaple.com.br/{slug}' if slug and not slug.startswith('http') else slug or URL
        start = (e.get('startDate') or e.get('start_at') or e.get('starts_at') or
                 e.get('startsAt') or e.get('date') or '')
        iso = ''
        if start:
            try:
                dt = datetime.fromisoformat(str(start).replace('Z', '+00:00')).astimezone()
                iso = dt.strftime('%Y-%m-%d')
            except Exception:
                iso = parse_iso(str(start))
        out.append({
            'name': name[:140],
            'detail': '',
            'date': fmt_date(iso),
            'time': '',
            'iso': iso,
            'venue': 'Casa Rockambole',
            'v': 'rockambole',
            'genre': 'Experimental / Rock / Noise',
            'price': '',
            'url': url,
        })
    return out


def _build_events(cards: list) -> list:
    """Build events from the structured card dicts extracted by JS or requests."""
    events, seen = [], set()
    for c in cards:
        href = (c.get('href') or '').strip()
        # Only accept event subpages: meaple.com.br/rockambole/<slug>
        if not re.match(r'https?://(?:www\.)?meaple\.com\.br/rockambole/.+', href):
            continue

        raw_text = c.get('text') or ''
        name = (c.get('name') or '').strip()

        # If no explicit name, derive from text lines (skip date-like lines)
        if not name:
            lines = [l.strip() for l in raw_text.split('\n') if l.strip() and len(l.strip()) > 2]
            for line in lines:
                if not re.search(r'\b\d{1,2}[/\s](?:de\s+)?(?:\d|jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)', line.lower()):
                    name = re.sub(r'\s+', ' ', line)[:140]
                    break
            if not name:
                name = re.sub(r'\s+', ' ', lines[0] if lines else raw_text)[:140]

        if len(name) < 3:
            continue

        # Prefer explicit date field; fall back to parsing full text
        iso = parse_iso(c.get('date') or '') or parse_iso(raw_text)

        key = (name.lower(), href)
        if key in seen:
            continue
        seen.add(key)

        events.append({
            'name': name,
            'detail': '',
            'date': fmt_date(iso),
            'time': (c.get('time') or '').strip(),
            'iso': iso,
            'venue': 'Casa Rockambole',
            'v': 'rockambole',
            'genre': 'Experimental / Rock / Noise',
            'price': (c.get('price') or '').strip(),
            'url': href,
        })
    return events


def _try_requests() -> list:
    res = requests.get(URL, headers=_HEADERS, timeout=20)
    res.raise_for_status()
    print(f'[rockambole] requests — {res.status_code}, {len(res.text)} bytes')
    soup = BeautifulSoup(res.text, 'html.parser')

    # Try __NEXT_DATA__ first
    tag = soup.find('script', id='__NEXT_DATA__')
    if tag and tag.string:
        try:
            raw = _find_events_json(json.loads(tag.string))
            if raw:
                events = _parse_json_events(raw)
                if events:
                    print(f'[rockambole] {len(events)} eventos via __NEXT_DATA__')
                    return events
        except Exception as ex:
            print(f'[rockambole] __NEXT_DATA__ parse error: {ex}')

    # Fallback: anchor links
    anchors = [
        {
            'href': a.get('href', ''),
            'text': a.get_text('\n', strip=True),
            'name': '',
            'date': '',
            'time': '',
            'price': '',
        }
        for a in soup.select('a[href*="meaple.com.br/rockambole/"]')
    ]
    return _build_events(anchors)


def _try_playwright() -> list:
    from playwright.sync_api import sync_playwright
    from scrapers._browser import stealth_page, goto_safe

    with sync_playwright() as p:
        browser, ctx, page = stealth_page(p)
        try:
            goto_safe(page, URL, timeout=30000)
            page.wait_for_timeout(5000)
            print(f'[rockambole] Playwright — title: {page.title()!r}')

            # Try __NEXT_DATA__ JSON
            try:
                nd = page.evaluate(
                    '() => { const s = document.getElementById("__NEXT_DATA__"); return s ? s.textContent : null; }'
                )
                if nd:
                    raw = _find_events_json(json.loads(nd))
                    if raw:
                        events = _parse_json_events(raw)
                        if events:
                            print(f'[rockambole] {len(events)} eventos via __NEXT_DATA__ (Playwright)')
                            return events
            except Exception as ex:
                print(f'[rockambole] __NEXT_DATA__ (Playwright): {ex}')

            # Scroll to trigger lazy load
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(2000)
            page.evaluate('window.scrollTo(0, 0)')
            page.wait_for_timeout(1000)

            # Extract structured card data via JS
            cards = page.evaluate(_EXTRACT_JS)
            events = _build_events(cards)
            print(f'[rockambole] {len(events)} eventos via Playwright DOM')
            return events
        finally:
            ctx.close()
            browser.close()


def get_casa_rockambole_events():
    try:
        events = _try_requests()
        if events:
            print(f'[rockambole] {len(events)} eventos via requests')
            return events
        print('[rockambole] requests OK mas sem eventos')
    except Exception as ex:
        print(f'[rockambole] requests falhou: {ex}')

    try:
        events = _try_playwright()
        if events:
            print(f'[rockambole] {len(events)} eventos via Playwright')
        return events
    except Exception as ex:
        print(f'[rockambole] Playwright falhou: {ex}')
        return []
