#!/data/data/com.termux/files/usr/bin/bash
# JARVIS Command Center - Startskript für dauerhaften Hintergrundbetrieb.
#
# Verhindert, dass Android den Prozess killt (termux-wake-lock),
# zeigt eine dauerhafte Benachrichtigung an (Pflicht für zuverlässigen
# Hintergrundbetrieb unter Android) und startet Backend + Telemetrie.

set -e
JARVIS_HOME="$HOME/jarvis-command-center"
LOG_DIR="$JARVIS_HOME/logs"
mkdir -p "$LOG_DIR"

echo "Starte JARVIS Command Center..."

# 1. CPU-Wake-Lock setzen, damit Termux im Hintergrund weiterläuft
termux-wake-lock

# 2. Persistente Benachrichtigung anzeigen (macht Android-seitig klar:
#    diese App läuft aktiv im Hintergrund, wird seltener gekillt)
termux-notification \
  --id jarvis-status \
  --title "JARVIS Command Center" \
  --content "Aktiv im Hintergrund - höre auf 'Jarvis'" \
  --ongoing \
  --priority high

# 3. FastAPI-Server im Hintergrund starten
cd "$JARVIS_HOME/backend"
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 \
  > "$LOG_DIR/server.log" 2>&1 &
SERVER_PID=$!
echo "Server gestartet (PID $SERVER_PID), Log: $LOG_DIR/server.log"

# Kurz warten, bis der Server bereit ist
sleep 3

# 4. Telemetrie-Bridge im Hintergrund starten
cd "$JARVIS_HOME/android-bridge"
nohup python telemetry_bridge.py > "$LOG_DIR/telemetry.log" 2>&1 &
TELEMETRY_PID=$!
echo "Telemetrie-Bridge gestartet (PID $TELEMETRY_PID)"

# 5. Wake-Word-Listener im Hintergrund starten
nohup python wakeword_listener.py > "$LOG_DIR/wakeword.log" 2>&1 &
WAKEWORD_PID=$!
echo "Wake-Word-Listener gestartet (PID $WAKEWORD_PID)"

# PIDs merken, damit stop_jarvis.sh sie sauber beenden kann
echo "$SERVER_PID $TELEMETRY_PID $WAKEWORD_PID" > "$JARVIS_HOME/.jarvis_pids"

echo "JARVIS läuft. Dashboard: http://127.0.0.1:8000"
echo "Zum Beenden: bash stop_jarvis.sh"
