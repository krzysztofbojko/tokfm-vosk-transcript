FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    wget \
    unzip \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir vosk

# Pobierz model Vosk dla języka polskiego
RUN mkdir -p /app/model && \
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip -O /tmp/model.zip && \
    unzip -q /tmp/model.zip -d /app/model && \
    mv /app/model/vosk-model-small-pl-0.22/* /app/model/ && \
    rmdir /app/model/vosk-model-small-pl-0.22 && \
    rm /tmp/model.zip

WORKDIR /app

COPY transkrybuj.py .

RUN mkdir -p /app/output

CMD ["python3", "-u", "transkrybuj.py"]
