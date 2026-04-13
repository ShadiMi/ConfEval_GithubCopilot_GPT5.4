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

## Local Development

### Infrastructure

Start PostgreSQL, Redis, and MinIO:

```bash
cd infrastructure
docker compose up -d
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
alembic upgrade head
python -m app.db.bootstrap
uvicorn app.main:app --reload
```

The initial Alembic revision now contains the first full schema migration for the current model layer.
External reviewer registration now requires a CV upload and stores the file under the configured local upload directory for admin review.
Student project submission and the admin project approval queue are now wired through the backend and frontend, including attachment download routes.
Admin users can now create tags, conferences, and sessions, and the protected catalog page reflects role-based conference and session visibility.
Students can now invite up to two team members on each project, and invited users can accept or decline pending team invitations from their dashboard.
Reviewers can now apply to sessions, and admins can approve or reject those applications from a dedicated queue.
Admins can now assign approved session reviewers to approved projects, reviewers can draft and submit scored evaluations, and project members can read completed reviews with reviewer names and criterion-level scores.
Authenticated users can now open an in-app notification inbox to review approval, assignment, and review events and mark them as read.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```
