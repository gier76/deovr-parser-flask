FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python packages
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    jinja2 \
    yt-dlp \
    requests \
    python-multipart

# Copy application code
COPY app/ /app/app/

# Expose the internal port
EXPOSE 8080

# Run the application
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
