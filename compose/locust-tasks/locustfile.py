from locust import HttpUser, between, task

import time


class QuickstartUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def hello_world(self):
        self.client.get("/chat", verify=False)
        self.client.get("/", verify=False)
        self.client.get("/register", verify=False)