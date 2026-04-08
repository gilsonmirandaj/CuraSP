#!/usr/bin/env python3
from __future__ import annotations
import json, os
from datetime import datetime, timezone

from sources.common import dedupe_events, sort_events
from sources.picles import fetch_events as fetch_picles
from sources.francisca import fetch_events as fetch_francisca
from sources.cine import fetch_events as fetch_cine
from sources.sesc import fetch_events as fetch_sesc
from sources.balaclava import fetch_events as fetch_balaclava
from sources.maldita import fetch_events as fetch_maldita
from sources.porta import fetch_events as fetch_porta
from sources.rockambole import fetch_events as fetch_rockambole
from sources.bona import fetch_events as fetch_bona
from fallback.static_events import FALLBACK_BY_SOURCE

SOURCES = [
    ('sesc', fetch_sesc),
    ('cine', fetch_cine),
    ('balaclava', fetch_balaclava),
    ('francisca', fetch_francisca),
    ('maldita', fetch_maldita),
    ('porta', fetch_porta),
    ('picles', fetch_picles),
    ('rockambole', fetch_rockambole),
    ('bona', fetch_bona),
]


def main():
    all_events = []
    report = []
    for source_name, fetcher in SOURCES:
        try:
            events = fetcher()
            if not events:
                raise RuntimeError('empty result')
            report.append({'source': source_name, 'count': len(events), 'mode': 'live_or_module'})
            all_events.extend(events)
        except Exception as ex:
            fallback = FALLBACK_BY_SOURCE.get(source_name, [])
            report.append({'source': source_name, 'count': len(fallback), 'mode': f'fallback: {ex}'})
            all_events.extend(fallback)

    deduped = sort_events(dedupe_events(all_events))
    output = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'events': deduped,
        'sources': report,
    }
    out_path = os.path.join(os.path.dirname(__file__), '..', 'events.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'[done] {len(deduped)} events written to events.json')

if __name__ == '__main__':
    main()
