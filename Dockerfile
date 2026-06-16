# Stage 1: build the React (Vite) frontend into app/static_dist.
FROM node:26-slim AS frontend-build

WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
# Vite outDir "../app/static_dist" -> /build/app/static_dist

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=5

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app

COPY pyproject.toml README.md ./
COPY app ./app

RUN python -m pip install --retries 5 --timeout 120 --upgrade pip \
    && python -m pip install --retries 5 --timeout 120 "." \
    && python -m pip install --retries 5 --timeout 120 --no-deps "mediapipe==0.10.21" \
    && python -m pip install --retries 5 --timeout 120 \
        "absl-py" \
        "attrs>=19.1.0" \
        "flatbuffers>=2.0" \
        "matplotlib" \
        "opencv-contrib-python<4.12" \
        "protobuf>=4.25.3,<5" \
        "sentencepiece" \
        "sounddevice>=0.4.4"

# Built SPA from the frontend stage, served by FastAPI at "/".
COPY --from=frontend-build /build/app/static_dist ./app/static_dist

ENV MPLCONFIGDIR=/tmp/matplotlib \
    XDG_CACHE_HOME=/tmp/.cache

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
