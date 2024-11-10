#!/bin/bash

# get current link
current=$(docker-compose exec nginx ls -la /etc/nginx/nginx.conf)

if [[ "$current" = *"green"* ]]; then
  echo "production is GREEN"
else
  echo "production is BLUE"
fi
