from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI(title="BloodLink API")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "database", "bloodlink.sqlite3")

def run_sql(query: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    result = [dict(row) for row in rows]
    conn.commit()
    conn.close()
    return columns, result

# Health router
health_router = APIRouter()

@health_router.get("/health/postgres")
async def postgres_health():
    return JSONResponse(content={"status": "ok", "database": "postgres"})

@health_router.get("/health/mongo")
async def mongo_health():
    return JSONResponse(content={"status": "ok", "database": "mongo"})

class QueryRequest(BaseModel):
    query: str

@health_router.post("/db/execute")
async def execute_query(req: QueryRequest):
    try:
        columns, rows = run_sql(req.query)
        return JSONResponse(content={"success": True, "columns": columns, "data": rows, "count": len(rows)})
    except Exception as e:
        return JSONResponse(status_code=400, content={"success": False, "error": str(e)})

app.include_router(health_router, prefix="/api")
