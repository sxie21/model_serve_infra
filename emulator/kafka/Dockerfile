FROM python:3.8-slim

WORKDIR /app 

COPY . /app

RUN pip install -r requirements.txt

ENV PROMETHEUS_PORT=9000 \
    KAFKA_TOPIC=training_data \
    KAFKA_HOST=kafka \
    KAFKA_PORT=9092

CMD ["python", "consumer.py"]