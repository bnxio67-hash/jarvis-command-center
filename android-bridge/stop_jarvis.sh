#!/data/data/com.termux/files/usr/bin/bash
# Beendet alle JARVIS-Hintergrundprozesse sauber.

JARVIS_HOME="$HOME/jarvis-command-center"
PID_FILE="$JARVIS_HOME/.jarvis_pids"

if [ -f "$PID_FILE" ]; then
  for pid in $(cat "$PID_FILE"); do
    kill "$pid" 2>/dev/null && echo "Prozess $pid beendet" || echo "Prozess $pid war schon beendet"
  done
  rm "$PID_FILE"
else
  echo "Keine laufenden JARVIS-Prozesse gefunden."
fi

termux-notification-remove jarvis-status
termux-wake-unlock

echo "JARVIS wurde vollständig gestoppt."
