FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir \
    flask \
    yt-dlp \
    requests

COPY app/ /app/app/

EXPOSE 8080

CMD ["python3", "app/main.py"]
