from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.schemas.task import TaskCreate, TaskResponse
from api.models.task import Task
from api.services.database import get_db
from api.services.queue import publish_task

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(type=task.type, params=task.params)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Publish to queue
    task_data = {
        "task_id": db_task.id,
        "type": db_task.type,
        "params": db_task.params
    }
    try:
        publish_task(task_data)
    except Exception as e:
        # Log error in production; for now, just raise it
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")
    
    return db_task

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task