from locust import SequentialTaskSet, task, User, between
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

class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        pass

    def on_stop(self):
        pass

    @task
    def get_liveness(self):
        invite = self.client.issuer_getliveness()

class Liveness(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"