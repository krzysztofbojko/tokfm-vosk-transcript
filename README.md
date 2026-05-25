# TOK FM Vosk Transcript

Transkrypcja na żywo strumienia radia TOK FM za pomocą [Vosk](https://alphacephei.com/vosk/) (offline speech recognition).

Uruchomione w kontenerze Docker na Raspberry Pi (aarch64).

## Pliki

- `Dockerfile` — obraz z Python 3.12, ffmpeg, Vosk + modelem `vosk-model-small-pl-0.22`
- `transkrybuj.py` — skrypt przechwytujący stream MP3, konwertujący do PCM i transkrybujący

## Budowanie

```bash
docker build -t tokfm-vosk .
```

## Uruchomienie

```bash
docker run -d --name tokfm-transkrypcja \
  --restart unless-stopped \
  -e TZ=Europe/Warsaw \
  -v $(pwd)/output:/app/output \
  tokfm-vosk
```

## Dane

Transkrypcje zapisywane są w `output/tokfm_RRRR-MM-DD_GG.txt` — jeden plik dziennie z timestampami.

## Strumień

TOK FM: `https://radiostream.pl/tuba10-1.mp3?dist=gra_www`
