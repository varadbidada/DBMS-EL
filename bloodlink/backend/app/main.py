from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

app = FastAPI(title="BloodLink API")

# Health router
health_router = APIRouter()

@health_router.get("/health/postgres")
async def postgres_health():
    # Placeholder: actual DB check will be implemented later
    return JSONResponse(content={"status": "ok", "database": "postgres"})

@health_router.get("/health/mongo")
async def mongo_health():
    # Placeholder: actual DB check will be implemented later
    return JSONResponse(content={"status": "ok", "database": "mongo"})

app.include_router(health_router, prefix="/api")
