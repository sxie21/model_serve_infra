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

1. install toolkits
    ```
    docker_install.sh (if needed)
    put model files(model.pth and model.py) under model_serve_infra/torchserve/ they already exists by default
    ```

2. To get everything all set:

    ```
    cd model_serve_infra
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
4. Once setup, a model is ready to serve at test environment http://localhost/test/predict
    ```
    curl -X POST http://localhost/test/predict -H "Content-Type: application/json" -d '{"data": [4.0,6.0]}'
    ```

6. (Optional) ssh to the server to view web UI(e.g grafana) on local PC
    ```
     ssh -L 9090:localhost:9090 -L 3000:localhost:3000 -L 8080:localhost:8080 username>@hostname -i your_ssh_key.pem
    ```

5. Start a simulator to generate user input and perform load test

    visit localhost:8089 on local browser
    replace with your host ip and start load test
    ![alt text](./assets/locust.png)


    then visit localhost:3000 on local browser, login with
    user: admin
    password: grafana
    and you can view the metrics on Grafana
    ![alt text](./assets/grafana.png)


6. Once feeling good, the model can be deployed to prod enviroment
    edit nginx config, choose the desired path for predict
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

    then use prod api is ready for serving:
    ```
    curl -X POST http://localhost/predict -H "Content-Type: application/json" -d '{"data": [4.0,6.0]}'
    ```



7. model update
    - upload new model file to torchserve/
    - check which instance is running in production
    ```

    ```
    - archive model on another instance

    ```
    # if service in running in torchserve_green, then:
    docker-compose exec torchserve_blue torch-model-archiver --model-name <model name> --version 1.0 --model-file model.py --serialized-file model.pth --handle handler.py --export-path model_store
    ```
    - serve the model
    ```
    # register model by torchserve api
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

## Now lets use CICD tools to automatically orchestrate model update

    install Jenkins
    ```
    
    ```




    ```
8. Check qps load and latency:
    ```
    test qps 
    sudo apt install apache2-utils

    ab -n 1000 -c 100 ttp://localhost:9000/predictions/<model name>
    这里，-n 1000 表示发送 1000 个请求，-c 100 表示使用 100 个并发请求，尽量维持目标 QPS。
    ```






docker torchserve
```
docker run --rm -it -p 8080:8080 -p 8081:8081 -v $PWD/model_store:/model_store pytorch/torchserve torchserve --model-store=/model_store --disable-token-auth
```


```
check exsiting models
curl http://localhost:8001/models 
```







chmod 644 ./models/config.properties
chmod 644 ./models/metrics.yaml



docker run --rm -it -p 8080:8080 -p 8081:8081 -v $PWD/model_store:/model_store pytorch/torchserve:latest torchserve --model-store ./model_store --models model=model1.mar --ncs


curl -H "Authorization: Bearer TvN_lu9W" http://localhost:8081/models


docker ps
docker exec -it <containerid> /bin/bash
       docker exec -it 3af2a3c4e3b9 /bin/bash





manage:
curl http://localhost:8001/models 
curl -X POST "http://localhost:8001/models?url=model1.mar&model_name=model1"
curl -X PUT "http://localhost:8001/models/model1?min_worker=1&max_worker=1"

inference:
curl -X POST http://localhost:8000/predictions/model0 -H "Content-Type: application/json" -d '{"data": [1, 2]}'

nginx:
curl -X POST http://localhost:/predictions/model1 -H "Content-Type: application/json" -d '{"data": [1, 2]}'



配置nginx后更新
docker-compose exec nginx nginx -s reload


torch-model-archiver --model-name model --version 1.0 --model-file model.py --serialized-file model.pth --handle handler.py --export-path model_store/green


torch-model-archiver --model-name model --version 1.0 --model-file /home/model-server/model.py --serialized-file /home/model-server/model.pth --handler /home/model-server/handler.py --export-path /home/model-server/model-store/green

curl -X POST "http://localhost:8001/models?url=model.mar&model_name=model"
curl -X PUT "http://localhost:8001/models/model?min_worker=1&max_worker=1"

curl -X POST http://localhost:8000/predictions/model0 -H "Content-Type: application/json" -d '{"data": [4.0, 6.0]}'

docker-compose logs --tail=25 torchserve_green

curl -X POST http://localhost/predict -H "Content-Type: application/json" -d '{"data": [4.0, 6.0]}'


curl -X POST "http://localhost:8001/models?url=model3.mar&model_name=model3"
curl -X PUT "http://localhost:8001/models/model3?min_worker=1&max_worker=1"
curl -X POST http://localhost:8000/predictions/model3 -H "Content-Type: application/json" -d '{"data": [4.0, 6.0]}'

curl -X POST "http://localhost:9001/models?url=model1.mar&model_name=model1"
curl -X PUT "http://localhost:9001/models/model1?min_worker=1&max_worker=1"
curl -X POST http://localhost:9000/predictions/model3 -H "Content-Type: application/json" -d '{"data": [4.0, 6.0]}'


curl -X POST "http://localhost:8001/models?url=modelnew.mar&model_name=modelnew"
curl -X PUT "http://localhost:8001/models/modelnew?min_worker=1&max_worker=1"
curl -X POST http://localhost:8000/predictions/modelnew -H "Content-Type: application/json" -d '{"data": [1.0, 1.0]}'


torch-model-archiver --model-name mnist --version 1.0 --model-file examples/image_classifier/mnist/mnist.py --serialized-file examples/image_classifier/mnist/mnist_cnn.pt --handler examples/custom_metrics/mnist_handler.py

scp -i .\SiyuEC2.pem  "C:/Users/Neil/Downloads/mnist_cnn.pt" ubuntu@34.229.122.114:/home/ubuntu/mlops/models/test




jenkins自动测qps
配置rate limiting
模拟输入错误
back up access log


docker run -d -p 8089:8089 mylocust


to tesk the api:
get host ip 

```
ip route | grep default | awk '{print $3}'
ip route | grep default
default via 172.31.16.1 dev enX0 proto dhcp src 172.31.20.55 metric 10
```
edit Dockerfile under /lucost
replace with localhost ip

Build image
docker build - t locust_api_test .
docker run -p 8089:8089 -d locust_api_test


grafana 


(sum(Requests2XX[5m]))
/
(sum(rate(Requests4XX[5m])) * 100

torch-model-archiver --model-name mnist --version 1.0 --model-file mnist.py --serialized-file mnist_cnn.pt --handler mnist_handler.py

curl -X DELETE http://localhost:8001/models/modelnew
curl -X POST "http://localhost:8001/models?url=modelnew.mar&model_name=modelnew"
curl -X PUT "http://localhost:8001/models/modelnew?min_worker=1&max_worker=1"

? curl -X POST "http://localhost:8001/models/modelnew?reload=true"



curl -X POST "http://localhost:8001/models?url=mnist.mar&model_name=mnist"
curl -X PUT "http://localhost:8001/models/mnist?min_worker=1&max_worker=1"



torch-model-archiver --model-name modelnew --version 1.0 --model-file model.py --serialized-file model.pth --handle handler.py --export-path model_store
    alteratively
    test qps 
    ```
    sudo apt install apache2-utils

    ab -n 1000 -c 100 ttp://localhost:9000/predictions/<model name>
    这里，-n 1000 表示发送 1000 个请求，-c 100 表示使用 100 个并发请求，尽量维持目标 QPS。
    ```

        ```
    # register model in prod enviroment by torchserve api
    curl -X POST "http://localhost:8001/models?url=model.mar&model_name=model"

    # assgin resources
    curl -X PUT "http://localhost:8001/models/model?min_worker=1&max_worker=1"
    
    # you can also unregister model from test enviroment by using torchserve api
    curl -X DELETE http://localhost:9001/models/modelnew
    ```