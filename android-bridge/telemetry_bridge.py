"""
JARVIS Telemetrie-Bridge für Termux (läuft direkt auf dem Handy).

Liest echte Hardware-Daten über Termux:API und die Linux-/proc/-Schnittstelle
aus (Termux läuft auf einem echten Linux-Kernel unter Android) und sendet sie
im Sekundentakt an den lokalen FastAPI-Server (localhost, da alles auf dem
gleichen Gerät läuft).

Voraussetzung: `pkg install termux-api` UND die Termux:API-App installiert.

Start manuell:
    python telemetry_bridge.py

Start dauerhaft im Hintergrund: siehe start_jarvis.sh (nutzt termux-wake-lock).
"""
from __future__ import annotations
import json
import subprocess
import time
import uuid
import httpx

API_BASE = "http://127.0.0.1:8000"
API_KEY = "jarvis-super-secret-2026"  # MUSS exakt zum Backend .env passen
DEVICE_ID = "handy-" + str(uuid.getnode())[-6:]
INTERVAL_SECONDS = 1.0


def _run_termux_cmd(cmd: str) -> dict:
    """Führt einen termux-api Befehl aus und parst das JSON-Ergebnis."""
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=5)
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except Exception:
        return {}


def get_cpu_per_core() -> list[float]:
    """Liest CPU-Auslastung pro Kern aus /proc/stat (zwei Messungen, Delta berechnen)."""
    def read_stat() -> list[list[int]]:
        with open("/proc/stat") as f:
            lines = [l for l in f.readlines() if l.startswith("cpu") and l[3].isdigit()]
        return [[int(x) for x in l.split()[1:]] for l in lines]

    first = read_stat()
    time.sleep(0.15)
    second = read_stat()

    usages = []
    for a, b in zip(first, second):
        idle_a, idle_b = a[3], b[3]
        total_a, total_b = sum(a), sum(b)
        delta_total = total_b - total_a
        delta_idle = idle_b - idle_a
        usage = 0.0 if delta_total == 0 else (1 - delta_idle / delta_total) * 100
        usages.append(round(usage, 1))
    return usages


def get_ram_mb() -> tuple[float, float]:
    """Liest RAM-Verbrauch aus /proc/meminfo."""
    values = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, val = line.split(":")
            values[key.strip()] = int(val.strip().split()[0])  # in kB

    total_mb = values.get("MemTotal", 0) / 1024
    available_mb = values.get("MemAvailable", 0) / 1024
    used_mb = total_mb - available_mb
    return round(used_mb, 1), round(total_mb, 1)


def get_battery() -> tuple[float, bool]:
    """Nutzt termux-battery-status (Termux:API)."""
    data = _run_termux_cmd("termux-battery-status")
    percent = float(data.get("percentage", 0))
    charging = data.get("status", "") == "CHARGING"
    return percent, charging


def get_network() -> tuple[float, float, str]:
    """
    Nutzt termux-wifi-connectioninfo für Link-Speed (Approximation, keine
    Echtzeit-Durchsatzmessung -- für echten Durchsatz müsste ein aktiver
    Download/Upload-Test laufen, was Datenvolumen kostet).
    """
    wifi = _run_termux_cmd("termux-wifi-connectioninfo")
    if wifi.get("supplicant_state") == "COMPLETED":
        link_speed = float(wifi.get("link_speed_mbps", 0) or 0)
        return link_speed, link_speed, "wifi"
    return 0.0, 0.0, "mobile"


def collect_payload() -> dict:
    ram_used, ram_total = get_ram_mb()
    battery_percent, charging = get_battery()
    net_down, net_up, net_type = get_network()

    return {
        "device_id": DEVICE_ID,
        "timestamp": time.time(),
        "cpu_percent_per_core": get_cpu_per_core(),
        "ram_used_mb": ram_used,
        "ram_total_mb": ram_total,
        "battery_percent": battery_percent,
        "battery_charging": charging,
        "network_down_mbps": net_down,
        "network_up_mbps": net_up,
        "network_type": net_type,
    }


def main() -> None:
    print(f"JARVIS Telemetrie-Bridge gestartet (Gerät: {DEVICE_ID})")
    with httpx.Client(timeout=5) as client:
        while True:
            payload = collect_payload()
            try:
                client.post(
                    f"{API_BASE}/api/telemetry/ingest",
                    json=payload,
                    headers={"X-API-Key": API_KEY},
                )
            except httpx.HTTPError as e:
                print(f"Sendefehler (Server läuft?): {e}")
            time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
