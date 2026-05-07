FROM python:3.13.13-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Se instalan dependencias en una etapa separada para mantener liviana la imagen final
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt


FROM python:3.13.13-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# El contenedor no corre como root
RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app app

COPY --from=builder /opt/venv /opt/venv
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations

USER app

EXPOSE 8080

# Cloud Run entrega el puerto en la variable PORT
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
