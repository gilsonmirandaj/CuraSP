"""
Helper: cria um contexto Playwright com stealth mode para evitar detecção de bot.
Usado por todos os scrapers que precisam renderizar JS.
"""
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

_STEALTH_SCRIPT = """
  Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
  Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
  Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR','pt','en-US','en']});
  window.chrome = {runtime: {}, loadTimes: function(){}, csi: function(){}, app: {}};
  Object.defineProperty(navigator, 'permissions', {
    get: () => ({query: () => Promise.resolve({state: 'granted'})})
  });
"""

LAUNCH_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-web-security',
    '--window-size=1280,720',
]

UA = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/122.0.0.0 Safari/537.36'
)


def stealth_page(playwright, headless=True) -> tuple:
    """Retorna (browser, context, page) com stealth aplicado."""
    try:
        from playwright_stealth import stealth_sync
        _has_stealth = True
    except ImportError:
        _has_stealth = False

    browser: Browser = playwright.chromium.launch(headless=headless, args=LAUNCH_ARGS)
    context: BrowserContext = browser.new_context(
        user_agent=UA,
        viewport={'width': 1280, 'height': 720},
        locale='pt-BR',
        timezone_id='America/Sao_Paulo',
        java_script_enabled=True,
        accept_downloads=False,
    )
    page: Page = context.new_page()
    page.add_init_script(_STEALTH_SCRIPT)

    if _has_stealth:
        stealth_sync(page)

    return browser, context, page


def goto_safe(page: Page, url: str, timeout: int = 30000):
    """Navega para URL tentando networkidle primeiro, depois domcontentloaded."""
    try:
        page.goto(url, wait_until='networkidle', timeout=timeout)
    except Exception:
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=timeout)
        except Exception:
            page.goto(url, timeout=timeout)
