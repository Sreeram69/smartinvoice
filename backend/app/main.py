from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.security import verify_api_key
from app.api.routes import health, items, documents, customers, ocr, backup

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Local Windows processing engine for SmartInvoice AI with Nothing OS design",
)

# CORS setup - restricted to trusted origins (localhost, Vercel frontend, and tunnel providers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_origin_regex=settings.CORS_ALLOW_ALL_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Public routes (health checks and service discovery)
app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["Health"])

# Protected routes (require valid X-API-Key header)
app.include_router(
    items.router,
    prefix=settings.API_V1_PREFIX + "/items",
    tags=["Items"],
    dependencies=[Depends(verify_api_key)],
)
app.include_router(
    documents.router,
    prefix=settings.API_V1_PREFIX + "/documents",
    tags=["Documents"],
    dependencies=[Depends(verify_api_key)],
)
app.include_router(
    customers.router,
    prefix=settings.API_V1_PREFIX + "/customers",
    tags=["Customers"],
    dependencies=[Depends(verify_api_key)],
)
app.include_router(
    ocr.router,
    prefix=settings.API_V1_PREFIX + "/ocr",
    tags=["OCR"],
    dependencies=[Depends(verify_api_key)],
)
app.include_router(
    backup.router,
    prefix=settings.API_V1_PREFIX + "/backup",
    tags=["Backup"],
    dependencies=[Depends(verify_api_key)],
)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} Local Backend",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "database": "sqlite_local",
    }
