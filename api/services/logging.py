import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("TaskPulse")

# Silence Pika logging
logging.getLogger("pika").setLevel(logging.WARNING)

logger.info("Logging initialized")