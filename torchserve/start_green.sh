#!/bin/bash

# mkdir /home/model-server/model-store/green
# chmod +rw /home/model-server/model-store/green

torch-model-archiver --model-name model_v1 \
                    --version 1.0 \
                    --model-file /home/model-server/model.py \
                    --serialized-file /home/model-server/model.pth \
                    --handler /home/model-server/handler.py \
                    --export-path /home/model-server/model-store/green


torchserve --start --model-store /home/model-server/model-store/green \
           --enable-model-api --ts-config /home/model-server/config.properties \
           --models model_v1.mar \
           --disable-token-auth