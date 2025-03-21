from prometheus_client import Counter, Histogram, Gauge

# Task counters
TASKS_TOTAL = Counter("taskpulse_tasks_total", "Total number of tasks submitted", ["type"])
TASKS_SUCCEEDED = Counter("taskpulse_tasks_succeeded", "Tasks completed successfully", ["type"])
TASKS_FAILED = Counter("taskpulse_tasks_failed", "Tasks failed after retries", ["type"])
TASKS_RETRIED = Counter("taskpulse_tasks_retried", "Tasks retried", ["type"])

# Processing time histogram
TASK_PROCESSING_TIME = Histogram(
    "taskpulse_task_processing_seconds",
    "Time spent processing tasks",
    ["type"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, float("inf")]
)

# In-flight gauge
TASKS_IN_FLIGHT = Gauge("taskpulse_tasks_in_flight", "Number of tasks currently being processed")