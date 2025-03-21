# TaskPulse

TaskPulse is a distributed task scheduling and execution system built with FastAPI, RabbitMQ, PostgreSQL, and Prometheus. It allows users to submit tasks, process them asynchronously with retry logic, and monitor their performance via metrics.

## Features
- **Task Submission**: Submit tasks via a REST API with optional scheduling.
- **Asynchronous Processing**: Tasks are queued in RabbitMQ and processed by a worker with retry and dead-letter queue (DLQ) support.
- **Monitoring**: Prometheus metrics track task success, failure, retries, and processing time.
- **Configuration**: Settings managed via `.env` files or environment variables.

## Prerequisites
- Python 3.10+
- PostgreSQL 13+
- RabbitMQ 3.x with management plugin
