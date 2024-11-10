FROM Python:3.9

WORKDIR /app 

COPY model.py /app/model.py
COPY handler.py /app/handler.py
COPY model.pth /app/model.pth
COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements 
RUN apt-get update && apt-get install -y default-jdk

ARG MODEL_VERSION=1.0.0
ARG MODEL_NAME=simple_model

RUN torch-model-archiver --model-name ${MODEL_NAME} \
    --version ${MODEL_VERSION}\
    --model-file model.py\
    --serialized-file model.pth\
    --handle handler.py\
    --export-path model_store

CMD ["torchserve", "--start", "--model-store", "/app/model_store", "--models", "simple_model=simple_model.mar", "--ncs"]
