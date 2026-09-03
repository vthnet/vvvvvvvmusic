FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
        unzip \
    && which ffmpeg \
    && which ffprobe \
    && ffmpeg -version \
    && ffprobe -version \
    && rm -rf /var/lib/apt/lists/*

# Install Deno - required by current yt-dlp YouTube extraction
RUN curl -fsSL https://deno.land/install.sh | sh \
    && ln -s /root/.deno/bin/deno /usr/local/bin/deno \
    && deno --version

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]