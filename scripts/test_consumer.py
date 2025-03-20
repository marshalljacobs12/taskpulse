import pika
import json

def callback(ch, method, properties, body):
    task_data = json.loads(body.decode())
    print(f"Received task: {task_data}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", port=5672, credentials=pika.PlainCredentials("guest", "guest"))
)
channel = connection.channel()
channel.queue_declare(queue="task_queue", durable=True)
channel.basic_consume(queue="task_queue", on_message_callback=callback)
print("Waiting for tasks. Press CTRL+C to exit.")
channel.start_consuming()