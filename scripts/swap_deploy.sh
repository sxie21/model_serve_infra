#!/bin/sh

# get current symlink
current=$(docker-compose exec nginx cat /etc/nginx/nginx.conf | grep "proxy_pass" | head -n 1)
echo $current

# conditionally deploy the other color
if [[ $current = *"green"* ]]; then
  echo "deploying BLUE"
  #docker-compose exec nginx ln -sf /etc/nginx/nginx_blue.conf /etc/nginx/nginx.conf
  curl -X POST http://localhost:9001/models/reload -d "model_name=model"
else
  echo "deploying GREEN"
  #docker-compose exec nginx ln -sf /etc/nginx/nginx_green.conf /etc/nginx/nginx.conf
  curl -X POST http://localhost:8001/models/reload -d "model_name=model"
fi

# have nginx reload the conf file
docker-compose exec nginx nginx -s reload