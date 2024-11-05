pipeline {
    agent any
    environment {
        MODEL_NAME = "model0"
        BASE_URL = "http://localhost/predictions"
        QPS_THRESHOLD = 100
        LATENCY_THRESHOLD = 200 // 200 ms
    }

    stages {
        stage('Model Archive') {
            steps {
                script {
                    echo "Starting model archiving..."
                    sh 'torch-model-archiver --model-name ${MODEL_NAME} --version 1.0 --model-file ./model.py --handler ./handler.py --export-path ./model_store'
                }
            }
        }

        stage('TorchServe Deployment') {
            steps {
                script {
                    echo "Starting TorchServe deployment..."
                    sh 'docker-compose up -d torchserve_green torchserve_blue'
                }
            }
        }

        stage('QPS Test') {
            steps {
                script {
                    echo "Testing QPS..."
                    // Run QPS test using wrk
                    def qpsResult = sh(script: "wrk -t2 -c100 -d30s ${BASE_URL}", returnStdout: true).trim()
                    echo "QPS Test Result: ${qpsResult}"
                    // Parse the output to get the QPS
                    def qps = qpsResult =~ /Requests/sec:\s+(\d+)/
                    def actualQps = qps ? qps[0][1].toInteger() : 0
                    if (actualQps < QPS_THRESHOLD) {
                        error "QPS test failed. Actual QPS: ${actualQps}, Threshold: ${QPS_THRESHOLD}"
                    }
                }
            }
        }

        stage('Latency Test') {
            steps {
                script {
                    echo "Testing Latency..."
                    // Run latency test using wrk or curl
                    def latencyResult = sh(script: "wrk -t2 -c100 -d30s ${BASE_URL}", returnStdout: true).trim()
                    echo "Latency Test Result: ${latencyResult}"
                    // Parse the output to get the latency
                    def latency = latencyResult =~ /Latency\s+(\d+\.\d+)ms/
                    def actualLatency = latency ? latency[0][1].toFloat() : 0
                    if (actualLatency > LATENCY_THRESHOLD) {
                        error "Latency test failed. Actual Latency: ${actualLatency}ms, Threshold: ${LATENCY_THRESHOLD}ms"
                    }
                }
            }
        }

        stage('Register Model') {
            steps {
                script {
                    echo "Registering model to TorchServe..."
                    // Assuming you've already got a script to handle model registration
                    sh 'curl -X POST http://localhost:8081/models?model_name=${MODEL_NAME}&url=${MODEL_NAME}.mar'
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    echo "Cleaning up..."
                    sh 'docker-compose down'
                }
            }
        }
    }
}
