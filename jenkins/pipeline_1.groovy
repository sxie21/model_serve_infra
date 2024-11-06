pipeline {
    agent any

    environment {
        // 定义一些环境变量
        IMAGE_API = 'flask-api' // API服务的Docker镜像
        IMAGE_LOCUST = 'locust-api-test' // Locust测试的Docker镜像

        LOCUST_CMD = 'locust -f locustfile.py --headless --users 100 --spawn-rate 10 --host=http://localhost:5000'
        QPS_THRESHOLD = 50  // 设置 QPS 阈值
        LATENCY_THRESHOLD = 2000  // 设置延迟阈值，单位为毫秒

    }

    stages {
        stage('Checkout Code') {
            steps {
                // 拉取代码（假设代码托管在Git仓库）
                git 'https://your-repository-url.git'
            }
        }

        stage('Build API Service Docker Image') {
            steps {
                script {
                    // 构建API服务Docker镜像
                    docker.build("${IMAGE_API}")
                }
            }
        }

        stage('Build Locust Docker Image') {
            steps {
                script {
                    // 构建Locust测试工具的Docker镜像
                    docker.build("${IMAGE_LOCUST}")
                }
            }
        }

        stage('Run API Service Container') {
            steps {
                script {
                    // 运行API服务容器
                    // 这里假设API服务监听在5000端口
                    apiContainer = docker.run("${IMAGE_API}", '-p 5000:5000')
                }
            }
        }

        stage('Run Locust Test') {
            steps {
                script {
                    // 运行Locust容器，并测试API性能
                    // 假设Locust在8089端口
                    locustContainer = docker.run(
                        "${IMAGE_LOCUST}", 
                        '-p 8089:8089 -e locustfile.py'
                    )
                    // 你也可以在此阶段配置Locust的参数，例如设置并发数、用户数等
                    // 假设Locust测试的URL是 http://localhost:5000
                }
            }
        }

        stage('Stop Containers') {
            steps {
                script {
                    // 停止容器
                    apiContainer.stop()
                    locustContainer.stop()
                }
            }
        }

        stage('Archive Test Results') {
            steps {
                // 在这个阶段，你可以把Locust的输出日志或测试报告归档
                // 例如，如果Locust产生的日志在路径 'locust-results/*.html'
                archiveArtifacts artifacts: 'locust-results/*.html', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            // 清理资源，确保即使构建失败也会停止容器
            try {
                apiContainer?.stop()
                locustContainer?.stop()
            } catch (e) {
                echo "Failed to stop containers: ${e}"
            }
        }
    }
}