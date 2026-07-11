# JARVIS Android-Bridge - Setup nur fürs Handy (Termux)

## 1. Grundinstallation

```bash
pkg update && pkg upgrade -y
pkg install python git termux-api clang libffi openssl rust -y
termux-setup-storage
```

Zusätzlich aus dem **F-Droid Store** installieren (echte Android-Apps, kein Termux-Befehl):
- **Termux:API** (Pflicht - Akku, Netzwerk, TTS, Mikrofon)
- **Termux:Boot** (optional - für Autostart nach Neustart)

## 2. Projekt kopieren & Abhängigkeiten installieren

```bash
cd ~/jarvis-command-center/backend
pip install -r requirements.txt        # Kern-Backend
cd ../android-bridge
pip install -r requirements-termux.txt # STT/Wake-Word Zusatzpakete
```

Hinweis: `openwakeword` und `vosk` brauchen beim ersten `pip install` etwas
Geduld (Kompilierung nativer Erweiterungen) - das ist normal.

## 3. Modelle herunterladen (einmalig)

```bash
mkdir -p ~/jarvis-command-center/models
cd ~/jarvis-command-center/models

# Deutsches Vosk-STT-Modell (klein, ~45 MB, offline-fähig)
wget https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
unzip vosk-model-small-de-0.15.zip
mv vosk-model-small-de-0.15 vosk-model-small-de

# openWakeWord: mitgelieferte Basismodelle laden lassen
python -c "import openwakeword; openwakeword.utils.download_models()"
```

**Wichtig zum Wake-Word "Jarvis":** Die mitgelieferten openWakeWord-Modelle
sind auf englische Wörter wie "alexa" oder "hey jarvis" (!) trainiert - "hey jarvis"
ist tatsächlich als fertiges Modell dabei. Für ein exaktes eigenes "Jarvis!"-Modell
müsstest du openWakeWord's Trainings-Notebook nutzen (eigene Audio-Samples nötig).
Für den Start empfehle ich, das mitgelieferte `hey_jarvis` Modell zu verwenden:
in `wakeword_listener.py` den Pfad `WAKEWORD_MODEL_PATH` entsprechend anpassen.

## 4. Backend-Konfiguration

```bash
cd ~/jarvis-command-center/backend
cp .env.example .env
nano .env   # API_KEY, ANTHROPIC_API_KEY eintragen
```

**Wichtig:** Der `API_KEY` in `.env` muss exakt dem Wert entsprechen, der in
`telemetry_bridge.py` und `wakeword_listener.py` unter `API_KEY = "..."` steht.

## 5. Manuell starten & testen

```bash
cd ~/jarvis-command-center/android-bridge
chmod +x start_jarvis.sh stop_jarvis.sh
bash start_jarvis.sh
```

Dann im Handy-Browser `http://127.0.0.1:8000/docs` öffnen - sollte die API-Doku zeigen.
Logs bei Problemen: `cat ~/jarvis-command-center/logs/server.log` (bzw. `telemetry.log`,
`wakeword.log`).

Beenden: `bash stop_jarvis.sh`

## 6. Autostart nach Neustart (mit Termux:Boot)

```bash
mkdir -p ~/.termux/boot
cp ~/jarvis-command-center/android-bridge/autostart.sh ~/.termux/boot/start-jarvis.sh
chmod +x ~/.termux/boot/start-jarvis.sh
```

## Bekannte Grenzen (ehrlich, nicht schöngeredet)

- **Akkuverbrauch**: Dauerhafte Mikrofon-Zyklen + Wake-Lock kosten spürbar Akku.
  Realistisch: mehrere Stunden Standby-Reduktion. Für Dauerbetrieb: Handy an
  Ladegerät oder Powerbank.
- **Erkennungsverzögerung**: ca. 0,5-2,5 Sek. durch das datei-basierte
  Aufnahmeverfahren von Termux:API (kein echter Audio-Stream möglich).
- **Android-Energiesparmodus**: In den Android-Einstellungen für Termux
  "Akkuoptimierung deaktivieren" setzen, sonst pausiert Android den Prozess
  nach einiger Zeit trotz Wake-Lock.
- **Kein echtes Custom-Wake-Word "Jarvis"** ohne eigenes Training - das
  mitgelieferte "hey_jarvis"-Modell ist der pragmatische Kompromiss.
