const { Kafka } = require('kafkajs');
const prometheus = require('prom-client');
const http = require('http');
const process = require('process');

// Prometheus metrics
const meanX1Metric = new prometheus.Gauge({
  name: 'train_input_mean_x1',
  help: 'Mean of x1 from training input data'
});

const varX1Metric = new prometheus.Gauge({
  name: 'train_input_var_x1',
  help: 'Variance of x1 of training input data'
});

const meanX2Metric = new prometheus.Gauge({
  name: 'train_input_mean_x2',
  help: 'Mean of x2 from training input data'
});

const varX2Metric = new prometheus.Gauge({
  name: 'train_input_var_x2',
  help: 'Variance of x2 of training input data'
});

// Welford's algorithm for calculating mean and variance
class Welford {
  constructor() {
    this.meanX1 = 0;
    this.meanX2 = 0;
    this.varX1 = 0;
    this.varX2 = 0;
    this.n = 0;
  }

  update(x1, x2) {
    this.n += 1;
    
    const deltaX1 = x1 - this.meanX1;
    this.meanX1 += deltaX1 / this.n;
    this.varX1 += deltaX1 * (x1 - this.meanX1);

    const deltaX2 = x2 - this.meanX2;
    this.meanX2 += deltaX2 / this.n;
    this.varX2 += deltaX2 * (x2 - this.meanX2);
  }

  getMeanAndVariance() {
    return [
      this.meanX1, 
      this.n > 1 ? this.varX1 / (this.n - 1) : 0,
      this.meanX2, 
      this.n > 1 ? this.varX2 / (this.n - 1) : 0
    ];
  }
}

// Kafka consumer setup
const createConsumer = () => {
  const kafka = new Kafka({
    clientId: 'consumer',
    brokers: [`${process.env.KAFKA_HOST}:${process.env.KAFKA_PORT}`]
  });

  const consumer = kafka.consumer({ groupId: 'trainingdata' });
  return consumer;
};

// Start HTTP server for Prometheus scraping
const startHttpServer = () => {
  const port = process.env.PROMETHEUS_PORT;
  http.createServer((req, res) => {
    if (req.url === '/metrics') {
      res.setHeader('Content-Type', prometheus.register.contentType);
      res.end(prometheus.register.metrics());
    } else {
      res.statusCode = 404;
      res.end();
    }
  }).listen(port, () => {
    console.log(`Prometheus server listening on port ${port}`);
  });
};

// Main function
const main = async () => {
  const welford = new Welford();
  const consumer = createConsumer();
  
  // Start Prometheus server
  startHttpServer();

  // Connect Kafka consumer and subscribe to topic
  await consumer.connect();
  await consumer.subscribe({ topic: process.env.KAFKA_TOPIC, fromBeginning: true });

  // Consume messages from Kafka
  await consumer.run({
    eachMessage: async ({ message }) => {
      const data = JSON.parse(message.value.toString());
      const x1 = data.x1;
      const x2 = data.x2;

      if (x1 !== undefined && x2 !== undefined) {
        welford.update(x1, x2);
        const [meanX1, varX1, meanX2, varX2] = welford.getMeanAndVariance();

        // Update Prometheus metrics
        meanX1Metric.set(meanX1);
        varX1Metric.set(varX1);
        meanX2Metric.set(meanX2);
        varX2Metric.set(varX2);
      }
    }
  });
};

main().catch(console.error);
