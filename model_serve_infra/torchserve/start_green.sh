#!/bin/bash

# archive model
torch-model-archiver --model-name model \
                    --version 1.0 \
                    --model-file /home/model-server/model.py \
                    --serialized-file /home/model-server/model.pth \
                    --handler /home/model-server/handler.py \
                    --export-path /home/model-server/model-store/green

# start instance and serve model
torchserve --start --model-store /home/model-server/model-store/green \
           --enable-model-api --ts-config /home/model-server/config.properties \
           --models model.mar \
           --disable-token-auth
