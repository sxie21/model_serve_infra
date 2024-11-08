#!/bin/bash

# get current route
current=$(docker-compose exec nginx cat /etc/nginx/nginx.conf | sed -n '/location \/predict/,/}/p' | grep "proxy_pass" | head -n 1)

# echo out the production deployment
if [[ $current = *"green"* ]]; then
  echo "production is GREEN"
else
  echo "production is BLUE"
fi
