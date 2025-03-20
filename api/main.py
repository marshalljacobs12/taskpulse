from fastapi import FastAPI
from api.services.database import init_db
from api.routes.tasks import router as tasks_router

app = FastAPI(
    title="TaskPulse",
    description="A distributed task scheduling and execution API",
    version="0.1.0"
)

app.include_router(tasks_router)

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/health")
async def health_check():
    return {"status": "ok"}