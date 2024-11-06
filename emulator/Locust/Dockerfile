FROM python:3.9

WORKDIR /app 

COPY . /app/

RUN pip install locust

EXPOSE 8089

#CMD ["locust", "-f", "locustfile.py", "--host", "http://172.31.20.55:8000"]
CMD ["locust", "-f", "locustfile.py", "--host", "http://172.31.20.55:8000", "--headless", "-u", "10", "-r", "1", "--run-time", "1m"]
