# ConfEval

ConfEval is a conference and poster evaluation management system for academic institutions.

## Workspace Layout

- `backend/`: FastAPI application, domain models, API routes, and tests
- `frontend/`: Next.js application for student, reviewer, and admin workflows
- `infrastructure/`: local development infrastructure definitions
- `docs/`: architecture and implementation notes

## Current Status

This repository contains the initial implementation foundation:

- monorepo structure
- backend application bootstrapping
- frontend application bootstrapping
- core domain enums and models
- authentication and RBAC skeleton
- reviewer approval with CV upload
- project submission and admin approval
- tag, conference, and session management foundations
- project team invitations and acceptance flows
- reviewer session applications and admin approval queue
- manual reviewer assignment to approved projects
- reviewer draft/submitted reviews against session criteria
- student and team-member visibility into completed reviews
- notification inbox with read and mark-all-read actions

## Planned Next Steps

1. Complete persistence migrations and repositories.
2. Implement registration, approval, and project workflows.
3. Add reporting, exports, and remaining admin flows.

## Running with Docker

Everything (Postgres, Redis, MinIO, the FastAPI backend and the Next.js frontend)
runs as containers via Docker Compose. No local Python or Node toolchain is
required.

All published host ports are the project defaults **+2** to avoid clashing with
anything you may already be running locally:

| Service          | Container port | Host port |
| ---------------- | -------------- | --------- |
| Frontend (Next)  | 3000           | **3002**  |
| Backend (FastAPI)| 8000           | **8002**  |
| Postgres         | 5432           | **5434**  |
| Redis            | 6379           | **6381**  |
| MinIO API        | 9000           | **9002**  |
| MinIO Console    | 9001           | **9003**  |

### Start the stack

```bash
cd infrastructure
docker compose up --build
```

The backend container automatically waits for Postgres, runs
`alembic upgrade head`, seeds reference data, then starts `uvicorn`.

Open:

- Frontend: <http://localhost:3002>
- Backend API: <http://localhost:8002/api/v1>
- Backend health: <http://localhost:8002/health>
- MinIO console: <http://localhost:9003> (user `minioadmin` / pass `minioadmin`)

### Stop the stack

```bash
cd infrastructure
docker compose down            # keep volumes
docker compose down -v         # also drop postgres/minio/upload volumes
```

### Common tasks

Tail logs for one service:

```bash
docker compose logs -f backend
```

Run an ad-hoc command (e.g. a new Alembic revision) inside the backend
container:

```bash
docker compose run --rm backend alembic revision --autogenerate -m "msg"
```

Run the backend test suite inside the container:

```bash
docker compose run --rm backend pip install -e .[dev]
docker compose run --rm backend pytest
```
