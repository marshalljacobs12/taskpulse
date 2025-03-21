import pika
import json
from api.config import settings

def get_connection():
    credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        credentials=credentials
    )
    try:
        connection = pika.BlockingConnection(parameters)
        print("Connected to RabbitMQ for publishing")
        return connection
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {str(e)}")
        raise

def publish_task(task_data: dict):
    connection = get_connection()
    channel = connection.channel()
    
    # Declare dead-letter exchange and queue
    channel.exchange_declare(exchange=settings.dlx_name, exchange_type="direct", durable=True)
    channel.queue_declare(queue=settings.dlq_name, durable=True)
    channel.queue_bind(queue=settings.dlq_name, exchange=settings.dlx_name, routing_key=settings.dlq_name)
    
    # Declare main queue with DLQ settings
    args = {"x-dead-letter-exchange": settings.dlx_name, "x-dead-letter-routing-key": settings.dlq_name}
    channel.queue_declare(queue=settings.queue_name, durable=True, arguments=args)
    print(f"Queue {settings.queue_name} declared with DLQ settings")
    
    print(f"Publishing task: {task_data}")
    channel.basic_publish(
        exchange="",
        routing_key=settings.queue_name,
        body=json.dumps(task_data).encode(),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print("Task published successfully")
    connection.close()