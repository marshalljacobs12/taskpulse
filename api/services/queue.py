import pika
import json

RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
QUEUE_NAME = "task_queue"
DLX_NAME = "dead_letter_exchange"
DLQ_NAME = "dead_letter_queue"

def get_connection():
    credentials = pika.PlainCredentials("guest", "guest")
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
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
    channel.exchange_declare(exchange=DLX_NAME, exchange_type="direct", durable=True)
    channel.queue_declare(queue=DLQ_NAME, durable=True)
    channel.queue_bind(queue=DLQ_NAME, exchange=DLX_NAME, routing_key=DLQ_NAME)
    
    # Declare main queue with DLQ settings
    args = {"x-dead-letter-exchange": DLX_NAME, "x-dead-letter-routing-key": DLQ_NAME}
    channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments=args)
    print(f"Queue {QUEUE_NAME} declared with DLQ settings")
    
    print(f"Publishing task: {task_data}")
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(task_data).encode(),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print("Task published successfully")
    connection.close()