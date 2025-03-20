from pydantic import BaseModel
from typing import Dict, Any, Optional
from api.models.task import TaskStatus
from datetime import datetime

class TaskCreate(BaseModel):
    type: str
    params: Dict[str, Any]
    schedule: Optional[str] = None  # Optional schedule field

class TaskResponse(BaseModel):
    id: int
    type: str
    params: Dict[str, Any]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    retries: int
    schedule: Optional[str] = None

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat()}