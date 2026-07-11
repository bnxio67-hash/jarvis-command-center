# JARVIS Command Center

Vollständige Architektur für ein persönliches KI-Command-Center auf Android.

## Ordnerstruktur

```
jarvis-command-center/
├── backend/                     # Modul 1: Core Backend & KI-Gehirn
│   ├── app/
│   │   ├── main.py               # FastAPI-Einstiegspunkt
│   │   ├── core/
│   │   │   ├── config.py         # Settings (.env)
│   │   │   ├── security.py       # API-Key-Absicherung
│   │   │   └── ws_manager.py     # WebSocket-Broadcast (Telemetrie/Sat/Chat)
│   │   ├── agents/
│   │   │   ├── brain.py          # LLM-Orchestrierung inkl. Tool-Calling-Loop
│   │   │   └── tools.py          # Tool-Registry (Telemetrie, Suche, Satelliten)
│   │   ├── services/
│   │   │   ├── search_service.py     # Websuche-Anbindung
│   │   │   └── telemetry_store.py    # In-Memory-Telemetriespeicher
│   │   ├── routers/
│   │   │   ├── chat.py           # /api/chat/command (Sprachbefehle)
│   │   │   ├── telemetry.py      # /api/telemetry/ingest + /ws/telemetry
│   │   │   ├── search.py         # /api/search/query
│   │   │   └── satellites.py     # /ws/satellites
│   │   └── models/schemas.py     # Pydantic-Datenmodelle
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                    # Modul 2: 4K-Dashboard mit CesiumJS (folgt)
├── android-bridge/              # Modul 4: Telemetrie-Skript für's Handy (folgt)
└── docs/                        # Architektur- und API-Dokumentation
```

## Setup (Backend)

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEY, API_KEY etc. eintragen
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Danach ist die interaktive API-Doku unter `http://<deine-lokale-ip>:8000/docs` erreichbar
(wichtig: Handy und Server müssen im selben WLAN sein, damit das Phone-Bridge-Skript und
das Dashboard den Server erreichen können).

## Wichtiger Hinweis zum Wake-Word

Das Wake-Word "Jarvis" ("Hey Jarvis"-Erkennung) läuft **client-seitig auf dem Handy**
(z.B. via Porcupine/openWakeWord in einer kleinen Android-Vordergrund-App), nicht im
Cloud-Backend – aus Datenschutz- und Akkugründen. Sobald das Wake-Word erkannt wird,
nimmt das Handy die Sprache lokal per STT auf und schickt nur den fertigen Text an
`POST /api/chat/command`. Die Antwort kommt als Text zurück und wird lokal per TTS
vorgelesen. Ich zeige dir das Wake-Word- und STT/TTS-Setup im nächsten Schritt (Modul 1b).

## Nächste Schritte

1. **Modul 1b**: Android Wake-Word + STT/TTS Integration (Kotlin/Python-Bridge)
2. **Modul 2**: CesiumJS 4K-Dashboard mit Live-TLE-Satellitentracking
3. **Modul 3**: Vollständiger Such-Agent (BeautifulSoup + Such-API + Zusammenfassung)
4. **Modul 4**: Kivy-Telemetrie-Bridge fürs Handy
