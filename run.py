from datetime import date


def run():
    # ... existing code ...
    events = dedupe(events)
    # Filter to remove past events
    today = date.today().isoformat()
    events = [event for event in events if event['iso_date'] >= today]
    events.sort(key=sort_key)
    # ... more existing code ...