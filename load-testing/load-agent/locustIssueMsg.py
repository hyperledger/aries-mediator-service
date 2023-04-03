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
        while not self.client.is_running():
            self.client.startup(withMediation=False)

        self.get_invite()

        self.accept_invite()

    def get_invite(self):
        invite = self.client.issuer_getinvite()
        self.invite = invite

    def accept_invite(self):
        self.client.ensure_is_running()

        connection = self.client.accept_invite(self.invite['invitation_url'])
        self.connection = connection

    def on_stop(self):
        self.client.shutdown()

    @task
    def msg_client(self):
        self.client.msg_client(self.invite['connection_id'])

class IssueMsg(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"