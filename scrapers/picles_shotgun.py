from playwright.sync_api import sync_playwright

URL = "https://shotgun.live/venues/picles/events"

def get_picles_events():
    events = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)

        page.wait_for_timeout(5000)

        cards = page.query_selector_all("a[href*='/events/']")

        for card in cards:
            try:
                link = card.get_attribute("href")
                title = card.inner_text()

                if link and "/events/" in link:
                    events.append({
                        "casa": "Picles",
                        "titulo": title.strip(),
                        "link": f"https://shotgun.live{link}"
                    })
            except:
                pass

        browser.close()

    return events
