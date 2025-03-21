from pydantic import BaseSettings, Field
from dotenv import load_dotenv
import os

# Load .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    # Database settings
    db_user: str = Field(default="taskpulse", env="DB_USER")
    db_password: str = Field(default="secret", env="DB_PASSWORD")
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="taskpulse_db", env="DB_NAME")

    # RabbitMQ settings
    rabbitmq_host: str = Field(default="localhost", env="RABBITMQ_HOST")
    rabbitmq_port: int = Field(default=5672, env="RABBITMQ_PORT")
    rabbitmq_user: str = Field(default="guest", env="RABBITMQ_USER")
    rabbitmq_password: str = Field(default="guest", env="RABBITMQ_PASSWORD")
    queue_name: str = Field(default="task_queue", env="QUEUE_NAME")
    dlx_name: str = Field(default="dead_letter_exchange", env="DLX_NAME")
    dlq_name: str = Field(default="dead_letter_queue", env="DLQ_NAME")

    # Worker settings
    max_retries: int = Field(default=3, env="MAX_RETRIES")

    # API settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    # Worker metrics port
    worker_metrics_port: int = Field(default=8001, env="WORKER_METRICS_PORT")

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()