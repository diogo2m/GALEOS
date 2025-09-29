FROM python:3.11-slim

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Dependências básicas + ferramentas para baixar e extrair
RUN apt update && apt install -y \
    curl \
    build-essential \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Baixa e instala o Prometheus (ajuste a versão se precisar)
ENV PROMETHEUS_VERSION=3.2.1
RUN curl -sSL "https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz" \
    | tar -xz -C /app \
    && mv /app/prometheus-${PROMETHEUS_VERSION}.linux-amd64 /app/prometheus

# Instala dependências Python
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root

# Copia o restante do código
COPY . /app

EXPOSE 8000 9090

# Sobe Prometheus + servidor HTTP + sua aplicação
CMD ["bash", "-c", "\
    set -e; \
    /app/prometheus/prometheus --config.file=/app/prometheus.yml --web.listen-address=':9090' & \
    python3 -m http.server 8000 --directory /app/public & \
    python3 /app/main.py & \
    wait -n"]

