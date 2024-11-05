from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def index(self):
        self.client.get("/")
    
    @task(2)
    def about(self):
        self.client.get("/about")
