from fastapi import APIRouter

from app.api.routes import applications, auth, conferences, health, notifications, projects, reviews, tags, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(applications.router, prefix="/reviewer-applications", tags=["reviewer-applications"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(conferences.router, prefix="/conferences", tags=["conferences"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
