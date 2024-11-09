## Introduction

This project is about build a dockerized infrastructure on a single node HTTP server to serve and monitor a simple machinel learning model.

![alt text](./assets/SchematicDiagram.png)

## Contents

- `assets/`: images and screenshots
- `config/`: config files mounted in Docker volume
  - `nginx/`: config file for nginx
    - `nginx.conf`: config router to blue/green environment and rate limiting
  - `grafana/`: config file for grafana
    - `dashabords\`: pre-build grafana dashboards in json
    - `datasource.yml`: define data sources from prometheus
    - `dashboards.yml`: define databoard path
  - `prometheus/`: config files for Prometheus
    - `prometheus.yml`: define datasources
    - `alert_rules.yml`: define alertings
- `emulator/`: simulate user input, and kafka topic producing training data
  - `kafka/`: kafka data streaming of training data
  - `locust/`: generate user inputs to the model api in test enviroment
- `scripts/`: automate scripts e.g.swap deploy enviroment
- `kafka/`: scripts to consumer training data from kafka for model-drift detection
- `torchserve/`: models and torchserve configs
  - `model.py`: mle delivery of model structure
  - `model.pth`: mle delivery of model parameters
  - `model_store`: archived model for torchserve
  - `metrics.yaml`：metrics logged by torchserve and consumed by prometheus
  - `config.properties`: configs for torchserve
- `docker-compose.yml`：Dockers for torchserve, nginx, prometheus, grafana etc.



## Getting Started

1. **Preparation**
    - Install Docker(if needed)
    ```
    ./docker_install.sh
    ```
    - Put model deliverables model.py and model.pth under model_serve_infra/torchserve/ 

2. **To get everything all set**:

    ```
    cd model_serve_infra/
    docker-compose up -d
    ```

    In this stage docker will:
    - Create two torchserve instance serving the models and logging the metrics simutaneously
    - Create an nginx to handle incoming traffic and choose which torchserve instance for blue green deployment
    - Create a node exporter for prometheus to monitor the server itself
    - Create a prometheus instance to collect metrics
    - Create a grafana instance with pre-build dashboards to visualize metrics
    - Create a kafka consumer to ingest training data and calculate the statistics for model-drift detection
    - Create a locust instance to perform load test of the torchserve api

3. **Check if services are built:**
    ```
    $ docker-compose ps

    >NAME                                   IMAGE                           COMMAND                  SERVICE            CREATED       STATUS             PORTS
    model_serve_infra-grafana-1            grafana/grafana                 "/run.sh"                grafana            2 hours ago   Up About an hour   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp
    model_serve_infra-locust-1             locustio/locust                 "locust -f /locust-t…"   locust             2 hours ago   Up 59 minutes      5557/tcp, 0.0.0.0:8089->8089/tcp, :::8089->8089/tcp
    model_serve_infra-nginx-1              nginx                           "/docker-entrypoint.…"   nginx              2 hours ago   Up About an hour   0.0.0.0:80->80/tcp, :::80->80/tcp
    model_serve_infra-torchserve_blue-1    pytorch/torchserve:0.12.0-cpu   "/usr/local/bin/dock…"   torchserve_blue    2 hours ago   Up About an hour   7070-7071/tcp, 0.0.0.0:9000->8080/tcp, [::]:9000->8080/tcp, 0.0.0.0:9001->8081/tcp, [::]:9001->8081/tcp, 0.0.0.0:9002->8082/tcp, [::]:9002->8082/tcp
    model_serve_infra-torchserve_green-1   pytorch/torchserve:0.12.0-cpu   "/usr/local/bin/dock…"   torchserve_green   2 hours ago   Up About an hour   7070-7071/tcp, 0.0.0.0:8000->8080/tcp, [::]:8000->8080/tcp, 0.0.0.0:8001->8081/tcp, [::]:8001->8081/tcp, 0.0.0.0:8002->8082/tcp, [::]:8002->8082/tcp
    node_exporter                          prom/node-exporter              "/bin/node_exporter"     node_exporter      2 hours ago   Up About an hour   0.0.0.0:9100->9100/tcp, :::9100->9100/tcp
    prometheus                             prom/prometheus                 "/bin/prometheus --c…"   prometheus         2 hours ago   Up About an hour   0.0.0.0:9090->9090/tcp, :::9090->9090/tcp
    ```
4. **Inference at test api `http://localhost/test/predict`**
    ```
    $ curl -X POST http://localhost/test/predict -H "Content-Type: application/json" -d '{"data": [0.2,0.6]}'

    > {
    "output": 0.6496530771255493
    }

    ```

5. **(Optional) ssh to the server to use web UI from local PC**
    if running a server on a virtual machine like EC2
    ```
     $ ssh -L 9090:localhost:9090 -L 3000:localhost:3000 -L 8089:localhost:8089 username>@hostname -i your_ssh_key.pem

     # port 9090 for Prometheus
     # port 3000 for Grafana
     # port 8089 for Locust
    ```

6. **Start a simulator to generate user input and perform load test**

    - Open a browser and visit localhost:8089
    
    - replace with your host ip and start load test 

    <img src="./assets/locust.png" alt="alt text" width="300" style="float: left; margin-right: 20px; margin-left: 20px;"/>
    <div style="clear: both;"></div>

    - visit localhost:3000 on local browser to view monitoring metrics on Grafana, login with:
        - user: admin
        - password: grafana
    
        In addition to server load and software performance metrics, to simulate model drift detection, there's a kafka emulator under `./emulator/kafka` producing training data x1,x2 and a consumer under `./kafka` to consume the data and calculate mean and variance incrementally
        
        run kafka producer by `docker-compose -f ./emulator/kafka docker-compose.yaml up -d`
        
        run kakfa consumer by `node ./kafka/consumer.js`

        Z-score of input feature x1 and x2 are calculated on Grafana together with other monitoring metrics

    <img src="./assets/grafana.png" alt="alt text" width="600" style="float: left; margin-right: 20px; margin-left: 20px;"/>
    <div style="clear: both;"></div>


7. **Once the application is functioning correctly, update the Nginx configuration to serve the production API**

    Stop the emulators
    Edit nginx config under `./config/nginx/nginx.conf`, and specify the desired routing path
    ```
    $ nano ./config/nginx/nginx.conf

    >
    location /predict {
        proxy_pass http://green/predictions/<model_name>;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /test/predict {
        proxy_pass http://blue/predictions/<model_name>;
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
    
    this will trigger a reload of Nginx configuration without disrupting active connections, this step can also performed under a model rollback scenario

    Then use production api for serving:
    ```
    $ curl -X POST http://localhost/predict -H "Content-Type: application/json" -d '{"data": [0.2,0.6]}'
    ```


8. **model update**
    - upload new model file(model.py, model.pth) to ./model_serve_infra/torchserve/
    - check which instance is running in production
        ```
        $ chmod +x ./scripts/which_is_production.sh
        $ ./scripts/which_is_production.sh

        > production is GREEN
        ```
        sample output:
        ```
        ubuntu@ip-172-31-29-243:~/model_serve_infra$ chmod +x ./scripts/which_is_production.sh
        ubuntu@ip-172-31-29-243:~/model_serve_infra$ ./scripts/which_is_production.sh
        production is GREEN"
        ```
    - archive model on another instance

    ```
    #e.g. if service in running in torchserve_green, then:
    docker-compose exec torchserve_blue torch-model-archiver --model-name model --version 1.0 --model-file /home/model-server/models/model.py --serialized-file /home/model-server/models/model.pth --handler /home/model-server/handler/handler.py --export-path /home/model-server/model-store/blue
    ```

    - register and serve the model
    ```
    # register model by torchserve api
    # port number for torchserve_blue is 9001, port number for torchserve_green is 8001
    $ curl -X POST "http://localhost:9001/models?url=<your_model.mar>&model_name=<model name>"

    # assign resources
    $ curl -X PUT "http://localhost:9001/models/<model name>?min_worker=1&max_worker=1"
    ```
    if using a different model name, then nginx has to be edited to point to the new model name
    
    - repeat step 5,6 and 7

curl -X POST "http://localhost:9001/models?url=model.mar&model_name=model"
curl -X PUT "http://localhost:9001/models/model?min_worker=1&max_worker=1"




## Now let's use CICD tools to automatically orchestrate model update




jenkins自动测qps
配置rate limiting
模拟输入错误
back up access log


docker-compose exec -it kafka kafka-topics.sh --bootstrap-server localhost:9092 --create --topic trainingdata
WARN[0000] /home/ubuntu/model_serve_infra/emulator/kafka/docker-compose.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
Created topic trainingdata.
ubuntu@ip-172-31-29-243:~/model_serve_infra/emulator/kafka$ docker-compose exec -it kafka kafka-topics.sh --list --bootstrap-server localhost:9092
WARN[0000] /home/ubuntu/model_serve_infra/emulator/kafka/docker-compose.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 


