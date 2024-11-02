#! /usr/bin/env bash

# Run migrations
alembic upgrade heads

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 