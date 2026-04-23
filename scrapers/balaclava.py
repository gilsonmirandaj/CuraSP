import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]
VENUE_URL = 'https://shotgun.live/organizations/balaclava'

PAGE_URLS = [
    'https://shotgun.live/organizations/balaclava',
    'https://shotgun.live/pt-br/organizations/balaclava',
]

_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'pt-BR,pt;q=0.9',
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
    for field in ('startDate','start_date','start_at','starts_at','startsAt','date'):
        v = e.get(field)
        if v:
            return str(v)
    return ''


def _find_events(obj, depth=0) -> list:
    if depth > 6:
        return []
    if isinstance(obj, list) and len(obj) > 0:
        first = obj[0]
        if isinstance(first, dict) and any(k in first for k in ('name','title','startDate','start_at','slug')):
            return obj
    if isinstance(obj, dict):
        for v in obj.values():
            r = _find_events(v, depth + 1)
            if r:
                return r
    return []


def _parse_raw(raw: list) -> list:
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
            'date': f"{DAYS_PT[(dt.weekday()+1)%7]} {dt.day:02d}/{dt.month:02d}",
            'time': f"{dt.hour:02d}h{dt.minute:02d}" if dt.minute else f"{dt.hour:02d}h",
            'iso': dt.strftime('%Y-%m-%d'),
            'venue': venue_name or 'Audio SP',
            'v': 'balaclava',
            'genre': infer_genre(name),
            'price': '',
            'url': f"https://shotgun.live/events/{slug}" if slug else VENUE_URL,
        })
    return out


def _try_requests(url: str) -> list:
    res = requests.get(url, headers=_HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    print(f'[balaclava] requests {url} — {res.status_code}, {len(res.text)} bytes')

    tag = soup.find('script', id='__NEXT_DATA__')
    if tag and tag.string:
        raw = _find_events(json.loads(tag.string))
        if raw:
            return _parse_raw(raw)

    for script in soup.find_all('script', type='application/json'):
        try:
            raw = _find_events(json.loads(script.string or ''))
            if raw:
                return _parse_raw(raw)
        except Exception:
            pass

    return []


def _try_playwright(url: str) -> list:
    from playwright.sync_api import sync_playwright
    from scrapers._browser import stealth_page, goto_safe

    with sync_playwright() as p:
        browser, ctx, page = stealth_page(p)
        try:
            goto_safe(page, url)
            page.wait_for_timeout(5000)
            print(f'[balaclava] Playwright — title: {page.title()!r}')

            try:
                nd = page.evaluate('() => { const s = document.getElementById("__NEXT_DATA__"); return s ? s.textContent : null; }')
                if nd:
                    raw = _find_events(json.loads(nd))
                    if raw:
                        return _parse_raw(raw)
            except Exception:
                pass

            anchors = page.eval_on_selector_all('a[href*="/events/"]', '''els => {
                const seen = new Set();
                return els.filter(el => {
                    if (seen.has(el.href)) return false;
                    seen.add(el.href);
                    return true;
                }).map(el => {
                    const card = el.closest("article,li,[class*=card],[class*=Card],[class*=event],[class*=Event]") || el;
                    return {
                        href: el.href,
                        name: (card.querySelector("h1,h2,h3,[class*=title],[class*=Title]")?.innerText || el.innerText || "").trim(),
                        date: (card.querySelector("time,[class*=date],[class*=Date]")?.innerText || "").trim(),
                        venue: (card.querySelector("[class*=venue],[class*=Venue]")?.innerText || "").trim(),
                    };
                }).filter(e => e.name && e.name.length > 3);
            }''')

            events = []
            for a in anchors:
                name = re.sub(r'\s+', ' ', a.get('name', '')).strip()[:140]
                if not name:
                    continue
                events.append({
                    'name': name,
                    'detail': '',
                    'date': '',
                    'time': '',
                    'iso': '',
                    'venue': a.get('venue') or 'Audio SP',
                    'v': 'balaclava',
                    'genre': infer_genre(name),
                    'price': '',
                    'url': a.get('href', VENUE_URL),
                })
            return events
        finally:
            ctx.close()
            browser.close()


def get_balaclava_events():
    for url in PAGE_URLS:
        try:
            events = _try_requests(url)
            if events:
                print(f'[balaclava] {len(events)} eventos via requests')
                return events
        except Exception as ex:
            print(f'[balaclava] requests falhou ({url}): {ex}')

    for url in PAGE_URLS:
        try:
            events = _try_playwright(url)
            if events:
                print(f'[balaclava] {len(events)} eventos via Playwright')
                return events
        except Exception as ex:
            print(f'[balaclava] Playwright falhou ({url}): {ex}')

    print('[balaclava] Nenhum evento coletado.')
    return []
