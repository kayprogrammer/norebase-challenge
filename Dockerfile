# Build stage
FROM python:3.12.7 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Create and activate virtual environment, then install dependencies
RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install -r requirements.txt

# Final stage
FROM python:3.12.7-slim
WORKDIR /app

# Copy virtual environment from the builder stage
COPY --from=builder /app/.venv .venv/
COPY . .

# Set PATH so the environment's executables are prioritized
ENV PATH="/app/.venv/bin:$PATH"

# Run Alembic migrations and start FastAPI
CMD ["sh", "-c", "alembic upgrade heads && fastapi run"]
