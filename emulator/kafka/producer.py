import time
import json
import random
from kafka import KafkaProducer
import os

KAFKA_TOPIC = os.environ['KAFKA_TOPIC']
KAFKA_HOST = os.environ['KAFKA_HOST']
KAFKA_PORT = os.environ['KAFKA_PORT']

def create_producer():
    server = f'''{KAFKA_HOST}:{KAFKA_PORT}'''
    producer = KafkaProducer(
        bootstrap_servers=server,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    return producer

def main():
    producer = create_producer()
    
    while True:
        x1 = random.uniform(0, 1)
        x2 = random.uniform(0, 1)
        data = {'x1': x1, 'x2': x2}
        producer.send(KAFKA_TOPIC, data)
        print(f"Sent: {data}")
        time.sleep(1)


if __name__ == '__main__':
    main()