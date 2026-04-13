# ConfEval Architecture

## Backend

- FastAPI API-first backend
- SQLAlchemy 2.0 ORM models
- PostgreSQL persistence
- JWT-based authentication with refresh tokens
- Role and ownership checks enforced in dependencies and services
- S3-compatible object storage abstraction for uploaded files

## Frontend

- Next.js App Router application
- Protected route groups by role
- Server-first data access for protected resources
- Client components reserved for forms, uploads, and live notification UX

## Security Priorities

- deny-by-default authorization
- unapproved and deactivated reviewer login denial
- strict request validation
- signed file access
- auditable admin actions
- rate-limited authentication endpoints
