FROM python:3.11-slim

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

RUN apt update && apt install -y curl build-essential

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root

COPY . /app

EXPOSE 8000

CMD ["bash", "-c", "set -e; /app/prometheus-3.2.1.linux-amd64/prometheus --config.file=/app/prometheus.yml --web.listen-address=':9090' & python3 -m http.server 8000 --directory /app/public & python3 /app/main.py & wait -n"]
