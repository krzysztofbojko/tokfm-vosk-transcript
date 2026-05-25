#!/usr/bin/env python3
"""
Transkrypcja strumienia radiowego TOK FM za pomocą Vosk.
Zapisuje wyniki do /app/output/ (volumen dockera).
"""

import subprocess
import sys
import json
import os
import time
from datetime import datetime
from pathlib import Path

import vosk

# ─── konfiguracja ───────────────────────────────────────────────
STREAM_URL = "https://radiostream.pl/tuba10-1.mp3?dist=gra_www"
MODEL_PATH = "/app/model"
OUTPUT_DIR  = Path("/app/output")
CHUNK_SIZE  = 4000          # bajtów na ramkę (~125ms przy 16kHz/16bit/mono)
SAMPLE_RATE = 16000       

# ─── ffmpeg ─────────────────────────────────────────────────────
FFMPEG_CMD = [
    "ffmpeg",
    "-loglevel", "error",            # ciszej
    "-reconnect", "1",               # auto-reconnect dla streamu
    "-reconnect_streamed", "1",
    "-reconnect_delay_max", "10",
    "-i", STREAM_URL,
    "-acodec", "pcm_s16le",          # 16-bit signed PCM
    "-ac", "1",                       # mono
    "-ar", str(SAMPLE_RATE),          # 16 kHz
    "-f", "s16le",                    # raw PCM bez nagłówka
    "pipe:1"                          #
]

# ─── pomocnicze ─────────────────────────────────────────────────
def plik_wyjściowy() -> Path:
    """Zwraca ścieżkę do pliku z datą (jeden plik na godzinę)."""
    teraz = datetime.now()
    nazwa = teraz.strftime("tokfm_%Y-%m-%d_%H.txt")   # plik dzienny
    return OUTPUT_DIR / nazwa


def zapisz_wiersz(plik: Path, tekst: str):
    """Dopisuje wiersz z timestampem do pliku, tworzy katalog jeśli trzeba."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(plik, "a", encoding="utf-8") as f:
        f.write(f"[{teraz}] {tekst}\n")


# ─── główna pętla ───────────────────────────────────────────────
def main():
    print(f"[init] Ładuję model z {MODEL_PATH}...", flush=True)
    model = vosk.Model(MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    recognizer.SetWords(True)  # zwracaj info o czasie każdego słowa

    print(f"[init] Model załadowany. Łączę ze streamem...", flush=True)
    print(f"[init] Zapis do: {OUTPUT_DIR}/", flush=True)

    while True:
        proc = None
        try:
            proc = subprocess.Popen(
                FFMPEG_CMD,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print(f"[stream] Połączono. Transkrybuję...", flush=True)

            while True:
                data = proc.stdout.read(CHUNK_SIZE)
                if not data:
                    break   # ffmpeg się zakończył

                if recognizer.AcceptWaveform(data):
                    # pełne zdanie gotowe
                    result = json.loads(recognizer.Result())
                    tekst = result.get("text", "").strip()
                    if tekst:
                        print(tekst, flush=True)
                        zapisz_wiersz(plik_wyjściowy(), tekst)
                else:
                    # częściowy wynik — tylko wypisz bez zapisu
                    partial = json.loads(recognizer.PartialResult())
                    czesc = partial.get("partial", "").strip()
                    if czesc:
                        print(f"  → {czesc}", end="\r", flush=True)

                # rotacja pliku co godzinę
                plik_wyjściowy()

        except KeyboardInterrupt:
            print("\n[stop] Zatrzymanie na żądanie.", flush=True)
            break
        except Exception as e:
            print(f"[błąd] {e}", flush=True)
        finally:
            if proc:
                proc.kill()
                proc.wait()

        # restart po awarii streamu
        print("[reconnect] Ponawiam za 2 sekund...", flush=True)
        time.sleep(2)
        recognizer.Reset()  # wyczyść stan recognizera


if __name__ == "__main__":
    main()
