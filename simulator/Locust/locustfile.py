from locust import HttpUser, task, between
import random
import logging

class APIUser(HttpUser):
    wait_time = between(1, 2)  # latency bewteen each request
    @task
    def predict(self):
        #randomly generating invalid input
        if random.random() < 0.5:  # 99 % valid
            data = [random.uniform(0, 1), random.uniform(0, 1)]
        else:
            data = [random.uniform(0, 1), random.uniform(0, 1), random.randint(1, 5)]

        response = self.client.post('/test/predict', json={"data": data})

        if response.status_code != 200:
            logging.info(f'''Request failed with status code {response.status_code}. Response message: "{response.json()['message']}" Data sent: {data}''')
