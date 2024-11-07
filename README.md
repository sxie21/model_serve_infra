## Introduction

This project is about build a dockerized infrastructure on a single node HTTP server to serve and monitor a simple machinel learning model.

![alt text](./assets/SchematicDiagram.png)

## Contents

- `assets/`: images and screenshots
- `config/`： config files mounted in Docker volume
  - `nginx/`: config file for nginx for blue green deployment
    - `nginx.conf`
  - `grafana/` : config files for Grafana
    - `dashabords\`: pre-build dashboards in json
    - `datasource.yml`
    - `dashboards.yml`
  - `prometheus/`: config files for Prometheus
    - `prometheus.yml`: 
    - `alert_rules.yml`: 
- `emulator/`: simulate user input, and kafka topic producing training data
  - `kafka/`: 
  - `locust/`: 
- `scripts/`: automate scripts e.g.swap deploy enviroment
- `torchserve/`: models and torchserve configs
  - `model.py`: 
  - `model.pth`: 
  - `model_store`: archived model for torchserve
  - `metrics.yaml`：metrics logged by torchserve and consumed by prometheus
  - `config.properties`: configs for torchserve
- `docker-compose.yml`：Dockers for torchserve, nginx, prometheus, grafana etc.



## Getting Started

1. Preparation
    - install docker(if needed)
    ```
    ./docker_install.sh
    ```
    - put model files(model.pth and model.py) under model_serve_infra/torchserve/ they already exists by default

2. To get everything all set:

    ```
    cd model_serve_infra/
    docker-compose up -d
    ```
    
    In this stage docker will:
    - create a torchserve instance serving the models and logging the metrics simutaneously
    - create an nginx to handle incoming traffic and perform rate limiting, as well as choose torchserve instances for blue green deployment
    - create a node exporter for prometheus to monitor server itself
    - create a prometheus instance to collect metrics
    - create a grafana instance with pre-build dashboards to visualize metrics
    - create a kafka consumer to ingest training data and calculate the statistics for model-drift detection
    - create a locust instance to perform load test of the torchserve api

3. check if services are built:
    ```
    docker ps
    ```
4. Once setup, a model is ready to serve at test environment http://```server ip```/test/predict
    ```
    curl -X POST http://localhost/test/predict -H "Content-Type: application/json" -d '{"data": [4.0,6.0]}'
    ```

5. (Optional) ssh to the server to view web UI(e.g grafana) on local PC
    ```
     ssh -L 9090:localhost:9090 -L 3000:localhost:3000 -L 8080:localhost:8080 username>@hostname -i your_ssh_key.pem
    ```

6. Start a simulator to generate user input and perform load test

    visit localhost:8089 on local browser
    
    replace with your host ip and start load test
    
    ![alt text](./assets/locust.png)


    then visit localhost:3000 on local browser, login with
    - user: admin
    - password: grafana
    
    and you can view the metrics on Grafana
    ![alt text](./assets/grafana.png)


7. Once feeling good, the model can be deployed to prod enviroment

    edit ./config/nginx/nginx.conf, choose the desired path for predict
    ```
        location /predict {
            proxy_pass http://green/predictions/model;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /test/predict {
            proxy_pass http://blue/predictions/model;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    ```
    after config changed, update nginx with
    ```
    docker-compose exec nginx nginx -s reload
    ```

    then production api is ready for serving:
    ```
    curl -X POST http://localhost/predict -H "Content-Type: application/json" -d '{"data": [4.0,6.0]}'
    ```



8. model update
    - upload new model file(model.py, model.pth) to torchserve/
    - check which instance is running in production
    ```

    ```
    - archive model on another instance

    ```
    #e.g. if service in running in torchserve_green, then:
    docker-compose exec torchserve_blue torch-model-archiver --model-name <model name> --version 1.0 --model-file model.py --serialized-file model.pth --handle handler.py --export-path model_store
    ```
    - register and serve the model
    ```
    # register model by torchserve api
    # port number for torchserve_blue is 9001, port number for torchserve_green is 8001
    curl -X POST "http://localhost:9001/models?url=<your_model.mar>&model_name=<model name>"

    # assgin resources
    curl -X PUT "http://localhost:9001/models/<model name>?min_worker=1&max_worker=1"
    ```
    - to step 5 and 6

8. model rollback
    edit nginx config
    after config changed, update nginx with 
    ```
    docker-compose exec nginx nginx -s reload
    ```

## Now let's use CICD tools to automatically orchestrate model update

    install Jenkins
    ```
    
    ```









```
check exsiting models
curl http://localhost:8001/models 
```












jenkins自动测qps
配置rate limiting
模拟输入错误
back up access log

