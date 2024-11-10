#!/bin/bash

# get current link
current=$(docker-compose exec nginx ls -la /etc/nginx/nginx.conf)
echo $current

# deploy the other color
if [[ "$current" = *"green"* ]]; then
  echo "deploying BLUE"
  docker-compose exec nginx ln -sf /etc/nginx/nginx_blue.conf /etc/nginx/nginx.conf
else
  echo "deploying GREEN"
  docker-compose exec nginx ln -sf /etc/nginx/nginx_green.conf /etc/nginx/nginx.conf
fi

# reload the conf file
docker-compose exec nginx nginx -s reload
