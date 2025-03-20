import os
import sys
from pathlib import Path

# Add the project root (TaskPulse/) to sys.path
project_root = Path(__file__).parent.parent  # Goes up from scripts/ to TaskPulse/
sys.path.append(str(project_root))

import pika
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.task import Task, TaskStatus
import time

DATABASE_URL = "postgresql://taskpulse:secret@localhost:5432/taskpulse_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
QUEUE_NAME = "task_queue"
MAX_RETRIES = 3

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def process_task(task_data, db, channel, method):
    task_id = task_data["task_id"]
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        print(f"Task {task_id} not found in database")
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    task.status = TaskStatus.RUNNING
    db.commit()
    print(f"Processing task {task_id}: {task_data['type']}")

    try:
        # Simulate work with a chance of failure
        if task_data["type"] == "fail_test":  # For testing failures
            raise ValueError("Simulated failure")
        time.sleep(5)
        task.status = TaskStatus.COMPLETED
        db.commit()
        print(f"Completed task {task_id}")
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Task {task_id} failed: {str(e)}")
        task.retries += 1
        if task.retries >= MAX_RETRIES:
            task.status = TaskStatus.FAILED
            db.commit()
            print(f"Task {task_id} failed after {MAX_RETRIES} retries")
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            task.status = TaskStatus.PENDING
            db.commit()
            # Requeue the task
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            print(f"Task {task_id} requeued (retry {task.retries}/{MAX_RETRIES})")

def callback(ch, method, properties, body):
    task_data = json.loads(body.decode())
    print(f"Received task: {task_data}")
    
    db_gen = get_db()
    db = next(db_gen)
    try:
        process_task(task_data, db, ch, method)
    finally:
        db.close()

def main():
    credentials = pika.PlainCredentials("guest", "guest")
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    print("Worker started. Waiting for tasks...")
    channel.start_consuming()

if __name__ == "__main__":
    main()