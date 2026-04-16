from playwright.sync_api import sync_playwright
from datetime import datetime
import re

URL = 'https://site.bileto.sympla.com.br/casadefrancisca/'
MONTHS = {'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12}
DAYS_PT = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]


def parse_iso(text: str) -> str:
    """Extrai data ISO a partir de texto em português (ex: '15 de abril')."""
    t = ' '.join((text or '').split()).lower()

    # Formato "DD de mês"
    m = re.search(r'(\d{1,2})\s+de\s+([a-zç]{3,})', t)
    if m:
        day = int(m.group(1))
        month = MONTHS.get(m.group(2)[:3])
        if month:
            now = datetime.now()
            year = now.year
            try:
                dt = datetime(year, month, day)
                # Se a data já passou neste ano, assume próximo ano
                if dt.date() < now.date() and month < now.month:
                    dt = datetime(year + 1, month, day)
                return dt.strftime('%Y-%m-%d')
            except Exception:
                pass

    # Formato DD/MM ou DD/MM/YYYY
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


def get_casa_francisca_events():
    try:
        return _scrape_playwright()
    except Exception as ex:
        print(f'[casa_francisca] Playwright falhou: {ex}')
        return []


def _scrape_playwright():
    events = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox'],
        )
        page = browser.new_page(
            user_agent=(
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        )

        try:
            page.goto(URL, wait_until='networkidle', timeout=30000)
        except Exception:
            # networkidle pode dar timeout em páginas pesadas — tenta domcontentloaded
            page.goto(URL, wait_until='domcontentloaded', timeout=30000)

        # Aguarda renderização do React/JS
        page.wait_for_timeout(3000)

        # Coleta todos os <a href> com texto visível
        anchors = page.eval_on_selector_all('a[href]', '''els => els.map(el => ({
            href: el.href || "",
            text: el.innerText || "",
            title: el.getAttribute("title") || "",
            ariaLabel: el.getAttribute("aria-label") || ""
        }))''')

        browser.close()

    for a in anchors:
        href = normalize_href(a.get('href', ''))

        # Aceita links de evento da Sympla/Bileto/Casa de Francisca
        if not any(k in href for k in ('sympla.com.br', 'bileto.sympla', 'casadefrancisca')):
            continue

        # Descarta links de navegação genéricos
        if href.rstrip('/') in {
            URL.rstrip('/'),
            'https://sympla.com.br',
            'https://www.sympla.com.br',
            'https://site.bileto.sympla.com.br',
        }:
            continue

        raw = ' '.join((a.get('text') or a.get('title') or a.get('ariaLabel') or '').split())
        if len(raw) < 4:
            continue

        iso = parse_iso(raw)

        # Primeira linha não vazia é o nome do evento
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
