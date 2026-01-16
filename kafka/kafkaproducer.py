from kafka import KafkaProducer
import json
import time
import random

# Kafka producer (local)
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    api_version=(3, 9, 0),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("Kafka producer started...")

while True:
    message = {
        "sensor_id": random.randint(1, 10),
        "speed": random.randint(20, 100),
        "volume": random.randint(1, 50),
        "timestamp": int(time.time())
    }

    producer.send("traffic-data", message)
    producer.flush()

    print("Sent:", message)
    time.sleep(1)
