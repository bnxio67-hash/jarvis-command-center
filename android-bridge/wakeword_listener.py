"""
JARVIS Wake-Word- und Sprachschleife für Termux.

WICHTIGER TECHNISCHER HINWEIS:
Termux:API bietet keinen echten Live-Mikrofon-Stream, sondern nimmt Audio nur
in Dateischnipseln auf (`termux-microphone-record -l <Sekunden>`). Deshalb
läuft dieser Listener in kurzen Zyklen: Aufnehmen -> Wake-Word prüfen ->
bei Treffer den eigentlichen Befehl aufnehmen -> STT -> an JARVIS-Backend
senden -> Antwort per TTS vorlesen -> von vorn.

Das bedeutet eine Erkennungsverzögerung von bis zu ~2,5 Sekunden nach dem
Sagen von "Jarvis" - für einen Cloud-Sprachassistenten ist das normal
und im Alltag kaum störend.

Benötigte Modelle (einmalig herunterladen, siehe README im android-bridge Ordner):
  - openWakeWord ONNX-Modell für "jarvis" (oder Custom-Training, s.u.)
  - Vosk deutsches STT-Modell (z.B. vosk-model-small-de-0.15)
"""
from __future__ import annotations
import json
import os
import subprocess
import time
import wave
import httpx
import numpy as np
from openwakeword.model import Model as WakeWordModel
from vosk import Model as VoskModel, KaldiRecognizer

API_BASE = "http://127.0.0.1:8000"
API_KEY = "jarvis-super-secret-2026"

WAKEWORD_CLIP = os.path.expanduser("~/jarvis-command-center/android-bridge/_wake_clip.wav")
COMMAND_CLIP = os.path.expanduser("~/jarvis-command-center/android-bridge/_command_clip.wav")
VOSK_MODEL_PATH = os.path.expanduser("~/jarvis-command-center/models/vosk-model-small-de")
WAKEWORD_MODEL_PATH = os.path.expanduser("~/jarvis-command-center/models/jarvis_wakeword.onnx")

WAKE_CLIP_SECONDS = 2.5
COMMAND_CLIP_SECONDS = 5.0
WAKEWORD_THRESHOLD = 0.5


def record_clip(path: str, seconds: float) -> None:
    """Nimmt über Termux:API eine WAV-Datei mit fester Länge auf."""
    subprocess.run(
        ["termux-microphone-record", "-f", path, "-l", str(seconds), "-e", "wav"],
        check=True,
        timeout=seconds + 5,
    )
    # termux-microphone-record läuft asynchron -> kurz warten, bis Datei fertig ist
    time.sleep(seconds + 0.3)
    subprocess.run(["termux-microphone-record", "-q"], check=False)  # sicherstellen, dass gestoppt


def wav_to_float_array(path: str) -> np.ndarray:
    with wave.open(path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    return audio


def speak(text: str) -> None:
    """Gibt Text über die Android-eigene TTS-Engine (Deutsch) aus."""
    subprocess.run(["termux-tts-speak", "-l", "de-DE", text], check=False)


def transcribe(path: str, recognizer: KaldiRecognizer) -> str:
    with wave.open(path, "rb") as wf:
        recognizer.Reset()
        while True:
            data = wf.readframes(4000)
            if not data:
                break
            recognizer.AcceptWaveform(data)
        result = json.loads(recognizer.FinalResult())
        return result.get("text", "").strip()


def send_to_brain(text: str) -> str:
    try:
        resp = httpx.post(
            f"{API_BASE}/api/chat/command",
            json={"text": text},
            headers={"X-API-Key": API_KEY},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("reply_text", "Ich konnte keine Antwort generieren.")
    except httpx.HTTPError as e:
        return f"Verbindung zum JARVIS-Server ist fehlgeschlagen: {e}"


def main() -> None:
    print("Lade Wake-Word- und Spracherkennungsmodelle ...")
    wake_model = WakeWordModel(wakeword_models=[WAKEWORD_MODEL_PATH])
    vosk_model = VoskModel(VOSK_MODEL_PATH)
    recognizer = KaldiRecognizer(vosk_model, 16000)

    print("JARVIS hört zu. Sag 'Jarvis', um ihn zu aktivieren.")
    while True:
        record_clip(WAKEWORD_CLIP, WAKE_CLIP_SECONDS)
        audio = wav_to_float_array(WAKEWORD_CLIP)

        predictions = wake_model.predict(audio)
        score = max(predictions.values()) if predictions else 0.0

        if score >= WAKEWORD_THRESHOLD:
            print(f"Wake-Word erkannt (Score {score:.2f})! Nehme Befehl auf ...")
            speak("Ja?")
            record_clip(COMMAND_CLIP, COMMAND_CLIP_SECONDS)
            text = transcribe(COMMAND_CLIP, recognizer)

            if not text:
                speak("Entschuldigung, ich habe nichts verstanden.")
                continue

            print(f"Erkannt: {text}")
            reply = send_to_brain(text)
            print(f"JARVIS antwortet: {reply}")
            speak(reply)


if __name__ == "__main__":
    main()
