# Shows SP

Agenda de shows em São Paulo — projeto refatorado em pastas.

## Estrutura

```
shows-sp-refatorado/
├── index.html
├── data/
│   └── events.json
└── scripts/
    └── update_events.py
```

## O que mudou

- `events.json` foi movido para `data/events.json`.
- `update_events.py` foi movido para `scripts/update_events.py`.
- O script foi ajustado para gravar a saída em `data/events.json`.
- A correção do link da Casa Rockambole já está aplicada.

## Rodar localmente

```bash
python3 scripts/update_events.py
python3 -m http.server
```

## Observação

Se o `index.html` atual estiver fazendo `fetch("events.json")`, troque para `fetch("data/events.json")`.


## Ajustes aplicados

- Links da Casa de Francisca padronizados para a página oficial da casa na Sympla e para a página de programação oficial.
