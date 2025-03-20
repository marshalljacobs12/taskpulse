from fastapi import FastAPI

app = FastAPI(
    title="TaskPulse",
    description="A distributed task scheduling and execution API",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}