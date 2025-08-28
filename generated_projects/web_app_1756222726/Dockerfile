```dockerfile
# Stage 1: Build the application
FROM python:3.11-slim-bullseye as builder

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry install --no-interaction --no-root

COPY . .
RUN poetry build

# Stage 2: Create a non-root user
FROM python:3.11-slim-bullseye

RUN groupadd -r appuser && useradd -r -g appuser -m appuser

WORKDIR /app

COPY --from=builder /app/dist/*.whl /app/
RUN pip install --no-cache-dir /app/*.whl

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s CMD curl --fail http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
