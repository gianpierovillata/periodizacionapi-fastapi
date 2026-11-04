FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Imagen para la suite de pytest: docker compose run --rm test
FROM base AS test

USER root
COPY requirements-dev.txt pytest.ini ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
USER appuser

CMD ["pytest"]

# Imagen de ejecucion por defecto. Debe ser la ultima etapa.
FROM base AS runtime
