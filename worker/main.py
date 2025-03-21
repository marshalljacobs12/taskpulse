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
from api.services.metrics import TASKS_SUCCEEDED, TASKS_FAILED, TASKS_RETRIED, TASK_PROCESSING_TIME, TASKS_IN_FLIGHT
from api.services.logging import logger
from prometheus_client import start_http_server
from threading import Thread
from api.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
        logger.warning(f"Task {task_id} not found in database")
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    task.status = TaskStatus.RUNNING
    db.commit()
    logger.info(f"Processing task {task_id}: {task_data['type']}")
    TASKS_IN_FLIGHT.inc()

    try:
        start_time = time.time()
        if task_data["type"] == "fail_test":
            raise ValueError("Simulated failure")
        time.sleep(5)
        task.status = TaskStatus.COMPLETED
        db.commit()
        logger.info(f"Completed task {task_id}")
        TASKS_SUCCEEDED.labels(type=task_data["type"]).inc()
        TASK_PROCESSING_TIME.labels(type=task_data["type"]).observe(time.time() - start_time)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        task.retries += 1
        TASKS_RETRIED.labels(type=task_data["type"]).inc()
        if task.retries >= settings.max_retries:
            task.status = TaskStatus.FAILED
            db.commit()
            logger.error(f"Task {task_id} failed after {settings.max_retries} retries, sent to DLQ")
            TASKS_FAILED.labels(type=task_data["type"]).inc()
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        else:
            task.status = TaskStatus.PENDING
            db.commit()
            delay = 2 ** task.retries
            logger.info(f"Task {task_id} requeued with {delay}s delay (retry {task.retries}/{settings.max_retries})")
            time.sleep(delay)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    finally:
        TASKS_IN_FLIGHT.dec()

def callback(ch, method, properties, body):
    task_data = json.loads(body.decode())
    logger.info(f"Received task: {task_data}")
    
    db_gen = get_db()
    db = next(db_gen)
    try:
        process_task(task_data, db, ch, method)
    finally:
        db.close()

def main():
    credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        credentials=credentials
    )
    try:
        connection = pika.BlockingConnection(parameters)
        logger.info("Worker connected to RabbitMQ")
    except Exception as e:
        logger.error(f"Worker failed to connect to RabbitMQ: {str(e)}")
        return
    channel = connection.channel()
    # No queue_declare here; assume API sets it up
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.queue_name, on_message_callback=callback)
    logger.info("Worker started. Waiting for tasks...")
    channel.start_consuming()

if __name__ == "__main__":
    # Start Prometheus metrics server on port 8001
    Thread(target=start_http_server, args=(settings.worker_metrics_port,), daemon=True).start()
    logger.info("Metrics server started on http://localhost:8001/metrics")
    main()