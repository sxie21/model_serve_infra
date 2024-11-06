import json
import prometheus_client
from kafka import KafkaConsumer
from prometheus_client import start_http_server
import os 

PROMETHEUS_POST_NUM = os.environ['PROMETHEUS_PORT']
KAFKA_TOPIC = os.environ['KAFKA_TOPIC']
KAFKA_HOST = os.environ['KAFKA_HOST']
KAFKA_PORT = os.environ['KAFKA_PORT']

# Welford's algorithm for calculating mean and variance without saving all data
class Welford:
    def __init__(self):
        self.mean_x1 = 0
        self.mean_x2 = 0
        self.var_x1 = 0
        self.var_x2 = 0
        self.n = 0

    def update(self, x1, x2):
        self.n += 1
        delta_x1 = x1 - self.mean_x1
        self.mean_x1 += delta_x1 / self.n
        self.var_x1 += delta_x1 * (x1 - self.mean_x1)

        delta_x2 = x2 - self.mean_x2
        self.mean_x2 += delta_x2 / self.n
        self.var_x2 += delta_x2 * (x2 - self.mean_x2)

    def get_mean_and_variance(self):
        return self.mean_x1, self.var_x1 / (self.n - 1) if self.n > 1 else 0, self.mean_x2, self.var_x2 / (self.n - 1) if self.n > 1 else 0

# Prometheus Metrics
mean_x1_metric = prometheus_client.Gauge('train_input_mean_x1', 'Mean of x1 from training input data')
var_x1_metric = prometheus_client.Gauge('train_input_var_x1', 'Variance of x1 of training input data')
mean_x2_metric = prometheus_client.Gauge('train_input_mean_x2', 'Mean of x2 from training input data')
var_x2_metric = prometheus_client.Gauge('train_input_var_x2', 'Variance of x2 of training input data')

# Kafka consumer setup
def create_consumer():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=f'{KAFKA_HOST:KAFKA_PORT}',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    return consumer

def main():
    welford = Welford()
    consumer = create_consumer()
    
    start_http_server(PROMETHEUS_POST_NUM)
    
    for message in consumer:
        data = message.value
        x1 = data.get('x1')
        x2 = data.get('x2')
        
        if x1 is not None and x2 is not None:
            welford.update(x1, x2)
            mean_x1, var_x1, mean_x2, var_x2 = welford.get_mean_and_variance()

            mean_x1_metric.set(mean_x1)
            var_x1_metric.set(var_x1)
            mean_x2_metric.set(mean_x2)
            var_x2_metric.set(var_x2)

if __name__ == '__main__':
    main()
