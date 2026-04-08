from scrapers.picles_shotgun import get_picles_events
from scrapers.casa_francisca import get_casa_francisca_events
import json
import os

def run():
    events = []

    events += get_picles_events()
    events += get_casa_francisca_events()

    os.makedirs("data", exist_ok=True)

    with open("data/events.json", "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"{len(events)} eventos coletados")

if __name__ == "__main__":
    run()
