#!/bin/bash

# archive model
torch-model-archiver --model-name regressor \
                    --version 1.0 \
                    --model-file /home/model-server/models/regressor/1.0/model.py \
                    --serialized-file /home/model-server/models/regressor/1.0/model.pth \
                    --handler /home/model-server/models/regressor/handler.py \
                    --config-file /home/model-server/models/regressor/1.0/model_config.yaml \
                    --export-path /home/model-server/model-store/

# start instance and serve model
torchserve --start --model-store /home/model-server/model-store/ \
           --enable-model-api --ts-config /home/model-server/config.properties \
           --models regressor.mar \
           --disable-token-auth
