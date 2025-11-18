from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import (
    auth, bonds, payments, reports, notifications,
    settings as settings_router, vouchers, exports,
    dashboard, members, payment_events, admin
)

# Create FastAPI app
app = FastAPI(
    title="Bond Management System API",
    description="API for managing bond purchases, coupon payments, and member portfolios",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Authentication
app.include_router(auth.router, prefix="/api/v1")

# Bond Management (original purchase system)
app.include_router(bonds.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")

# Bond Issues System (new cooperative system)
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(members.router, prefix="/api/v1")
app.include_router(payment_events.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# Reporting & Utilities
app.include_router(reports.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(settings_router.router, prefix="/api/v1")
app.include_router(vouchers.router, prefix="/api/v1")
app.include_router(exports.router, prefix="/api/v1")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Bond Management System API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
