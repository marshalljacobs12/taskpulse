from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.orm import Session
from api.models.task import Task, TaskStatus
from api.services.queue import publish_task
from datetime import datetime
import pytz

scheduler = AsyncIOScheduler(timezone=pytz.UTC)

def schedule_task(task: Task, db: Session):
    task_data = {
        "task_id": task.id,
        "type": task.type,
        "params": task.params
    }

    def job():
        if task.status == TaskStatus.PENDING:
            publish_task(task_data)
            print(f"Scheduled task {task.id} queued at {datetime.utcnow()}")

    if task.schedule:
        try:
            # Try parsing as ISO datetime (one-time task)
            run_date = datetime.fromisoformat(task.schedule.replace("Z", "+00:00"))
            scheduler.add_job(job, trigger=DateTrigger(run_date=run_date), id=f"task_{task.id}")
        except ValueError:
            # Assume cron expression (recurring task)
            scheduler.add_job(job, trigger=CronTrigger.from_crontab(task.schedule), id=f"task_{task.id}")
        print(f"Scheduled task {task.id} with {task.schedule}")

def load_scheduled_tasks(db: Session):
    tasks = db.query(Task).filter(Task.status == TaskStatus.PENDING, Task.schedule.isnot(None)).all()
    for task in tasks:
        schedule_task(task, db)

def start_scheduler():
    scheduler.start()
    print("Scheduler started")