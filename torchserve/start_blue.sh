#!/bin/bash

torch-model-archiver --model-name model_v1 \
                    --version 1.0 \
                    --model-file /home/model-server/model.py \
                    --serialized-file /home/model-server/model.pth \
                    --handler /home/model-server/handler.py \
                    --export-path /home/model-server/model-store/blue


torchserve --start --model-store /home/model-server/model-store/blue \
           --enable-model-api --ts-config /home/model-server/config.properties \
           --model_name model_v1 \
           --disable-token-auth