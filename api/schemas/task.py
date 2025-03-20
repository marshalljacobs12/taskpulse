from pydantic import BaseModel
from typing import Dict, Any
from api.models.task import TaskStatus
from datetime import datetime

class TaskCreate(BaseModel):
    type: str
    params: Dict[str, Any]

class TaskResponse(BaseModel):
    id: int
    type: str
    params: Dict[str, Any]
    status: TaskStatus
    created_at: datetime  # Will be ISO format from datetime
    updated_at: datetime
    retries: int

    class Config:
        orm_mode = True  # Allows conversion from SQLAlchemy model
        json_encoders = {  # Ensures datetime is serialized to ISO format in JSON
            datetime: lambda v: v.isoformat()
        }