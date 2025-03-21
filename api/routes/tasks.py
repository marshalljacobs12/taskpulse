from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.schemas.task import TaskCreate, TaskResponse
from api.models.task import Task, TaskStatus
from api.services.database import get_db
from api.services.queue import publish_task
from api.services.scheduler import schedule_task
from api.services.metrics import TASKS_TOTAL
from api.services.logging import logger
from typing import List

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(type=task.type, params=task.params, schedule=task.schedule)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    TASKS_TOTAL.labels(type=task.type).inc()
    logger.info(f"Task created: id={db_task.id}, type={task.type}, schedule={task.schedule}")
    
    task_data = {
        "task_id": db_task.id,
        "type": db_task.type,
        "params": db_task.params
    }
    if db_task.schedule:
        try:
            schedule_task(db_task, db)
            logger.info(f"Task {db_task.id} scheduled")
        except Exception as e:
            logger.error(f"Failed to schedule task {db_task.id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to schedule task: {str(e)}")
    else:
        try:
            publish_task(task_data)
            logger.info(f"Task {db_task.id} queued")
        except Exception as e:
            logger.error(f"Failed to queue task {db_task.id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")
    
    return db_task

@router.get("/failed", response_model=List[TaskResponse])
async def get_failed_tasks(db: Session = Depends(get_db)):
    failed_tasks = db.query(Task).filter(Task.status == TaskStatus.FAILED).all()
    logger.info(f"Retrieved {len(failed_tasks)} failed tasks")
    return failed_tasks

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        logger.warning(f"Task {task_id} not found")
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info(f"Retrieved task {task_id}")
    return task
