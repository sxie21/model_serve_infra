import random
import time
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  
)

while True:
    x1 = random.uniform(0, 1)
    x2 = random.uniform(0, 1)
    
    message = {
        'x1': x1,
        'x2': x2
    }

    producer.send('training_data', value=message)

    print(f"Sent: {message}")

    time.sleep(1)
