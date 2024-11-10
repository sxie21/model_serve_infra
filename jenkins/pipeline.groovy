pipeline{
    agent any
    environment {
        WORK_DIR = "/home/ubuntu/model_serve_infra"
    }    
    stages{
        stage('Archive Model'){
            steps{
                script{
                    //variables define
                    def targetEnv = ""
                    def port = ""                    
                    
                    //get current serving environment
                    def currentEnv = sh(script: '''
                        cd "${WORK_DIR}/scripts"
                        ./which_is_production.sh
                    ''', returnStdout: true).trim()

                    echo "Current Environment: ${currentEnv}"
                    
                    //set targeting environment and port
                    if (currentEnv == "production is GREEN") {
                        targetEnv = "green"
                        port = "8001"
                    } else if (currentEnv == "production is BLUE") {
                        targetEnv = "blue"
                        port = "9001"                       
                    } else {
                        error "Unknown environment: ${currentEnv}"
                    }        

                    //archive model
                    echo "Archiving and test model in ${targetEnv} environment"
                    sh """
                        cd ${WORK_DIR}
                        docker-compose exec torchserve_${targetEnv} torch-model-archiver --model-name model --version 1.0 --model-file /home/model-server/model.py --serialized-file /home/model-server/model.pth --handler /home/model-server/handler.py --export-path /home/model-server/model-store/${targetEnv} -f
                        curl -X POST "http://localhost:${port}/models?url=model.mar&model_name=model"
                        curl -X PUT "http://localhost:${port}/models/model?min_worker=1&max_worker=1"
                        """
                }
            }
        }
        
        stage('Run wkr Test'){
            steps{
                script{
                    //perform load test by wrk
                    def result = sh(script: '''
                        cd ${WORK_DIR}/jenkins
                        wrk -t2 -c10 -d3s -s post.lua http://localhost/test/predict
                        ''', returnStdout: true).trim()
                    echo "wrk Test Result: ${result}"
                
                    //parse wrk results
                    def qps = result =~ /Requests\/sec:\s+(\d+)/
                    def latency = result =~ /Latency:\s+(\d+)\s+ms/
                    def actualQps = qps ? qps[0][1].toInteger() : 0
                    def avgLatency = latency ? latency[0][1].toInteger() : 0
                    echo "Actual QPS: ${actualQps}, Avg Latency: ${avgLatency} ms"
                    def qpsThreshold = 100
                    def latencyThreshold = 200
                    if (actualQps >= qpsThreshold && avgLatency <= latencyThreshold) {
                        echo "Test passed: QPS >= 100 and Latency <= 200ms"
                        return
                    } else {
                        error "Test failed: QPS < 100 or Latency > 200ms"
                    }
                }
            }
        }  
        
        stage('Swap Deploy') {
            steps {
                script {
                    sh """
                        cd ${WORK_DIR}/scripts
                        ./swap_deploy.sh
                    """
                }
            }
        }        
    }
}
