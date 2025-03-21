import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Depends
from api.services.database import init_db
from api.routes.tasks import router as tasks_router
from api.services.scheduler import start_scheduler, load_scheduled_tasks
from sqlalchemy.orm import Session
from api.services.database import get_db
from prometheus_client import make_asgi_app
from api.config import settings
# do I need logger? 

app = FastAPI(
    title="TaskPulse",
    description="A distributed task scheduling and execution API",
    version="0.1.0"
)

app.include_router(tasks_router)
app.mount("/metrics", make_asgi_app())  # Expose Prometheus metrics

@app.on_event("startup")
async def startup_event():
    init_db()
    db = next(get_db())
    load_scheduled_tasks(db)
    start_scheduler()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)