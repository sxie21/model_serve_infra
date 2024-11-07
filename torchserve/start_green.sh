#!/bin/bash


# torch-model-archiver --model-name model \
#                     --version 1.0 \
#                     --model-file /home/model-server/model.py \
#                     --serialized-file /home/model-server/model.pth \
#                     --handler /home/model-server/handler.py \
#                     --export-path /home/model-server/model-store/green


torchserve --start --model-store /home/model-server/model-store/green \
           --enable-model-api --ts-config /home/model-server/config.properties \
           --disable-token-auth