#!/data/data/com.termux/files/usr/bin/bash
# Wird von der Termux:Boot-App automatisch nach jedem Geräte-Neustart ausgeführt.
# Installation: Termux:Boot App installieren (aus F-Droid), dann diese Datei
# nach ~/.termux/boot/start-jarvis.sh kopieren:
#   mkdir -p ~/.termux/boot
#   cp autostart.sh ~/.termux/boot/start-jarvis.sh
#   chmod +x ~/.termux/boot/start-jarvis.sh

termux-wake-lock
bash ~/jarvis-command-center/android-bridge/start_jarvis.sh
