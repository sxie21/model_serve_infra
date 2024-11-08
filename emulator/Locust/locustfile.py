from locust import HttpUser, task, between
import os
import random

class APIUser(HttpUser):
    wait_time = between(1, 2)  # latency bewteen each request

    @task
    def predict(self):
        x1 = random.uniform(0, 1)
        x2 = random.uniform(0, 1)
        
        response = self.client.post('/test/predict', json={"data":[x1,x2]})
        
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
