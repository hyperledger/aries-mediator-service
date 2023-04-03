from locust import TaskSet, task, User, between
from locustClient import CustomClient
import time
import inspect
import json

import fcntl
import os
import signal

class CustomLocust(User):
    abstract = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.client = CustomClient(self.host)

class UserBehaviour(TaskSet):
    def on_start(self):
        self.client.startup()
        
    def on_stop(self):
        self.client.shutdown()

    @task
    def ping_mediator(self):
        self.client.ensure_is_running()

        self.client.ping_mediator()

class MediatorPing(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"