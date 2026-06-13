#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] waiting for postgres at ${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}..."
python - <<'PY'
import os
import socket
import time

host = os.environ.get("POSTGRES_HOST", "postgres")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
deadline = time.time() + 60
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit(f"postgres at {host}:{port} not reachable")
PY

echo "[entrypoint] running alembic migrations..."
alembic upgrade head

echo "[entrypoint] seeding reference data..."
python -m app.db.bootstrap || true

echo "[entrypoint] starting: $*"
exec "$@"
