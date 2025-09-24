# ---------- Build stage ----------
FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no-dev --no-interaction --no-ansi

COPY . /app/

# ---------- Runtime stage ----------
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app

RUN mkdir -p /vol/web/media
VOLUME /vol/web/media

EXPOSE 8000

CMD ["gunicorn", "tsu_posthub_api.wsgi:application", "--bind", "0.0.0.0:8000"]