from locust import TaskSet, task, User, between, Locust, events
import time
import inspect
import json

import fcntl
import os
import signal

from gevent import subprocess
from gevent import select

SHUTDOWN_TIMEOUT_SECONDS=10
READ_TIMEOUT_SECONDS=120
ERRORS_BEFORE_RESTART=10

def stopwatch(func):
    def wrapper(*args, **kwargs):
        # get task's function name
        previous_frame = inspect.currentframe().f_back
        _, _, task_name, _, _ = inspect.getframeinfo(previous_frame)

        start = time.time()
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            total = int((time.time() - start) * 1000)
            events.request_failure.fire(request_type="TYPE",
                                        name=task_name,
                                        response_time=total,
                                        exception=e,
                                        response_length=0)
        else:
            total = int((time.time() - start) * 1000)
            events.request_success.fire(request_type="TYPE",
                                        name=task_name,
                                        response_time=total,
                                        response_length=0)
        return result

    return wrapper

class CustomClient:
    def __init__(self, host):
        self.host = host
        self.agent = None
        self.errors = 0

    _locust_environment = None

    @stopwatch
    def startup(self):
        try:
            self.errors = 0
            self.agent = subprocess.Popen(['node', 'agent.js'], 
                bufsize=0,
                universal_newlines=True, 
                stdout=subprocess.PIPE, 
                stdin=subprocess.PIPE,
                shell=False)

            self.run_command({"cmd":"start"})

            line = self.readjsonline()

            # we tried to start the agent and failed
            if self.agent is None or self.agent.poll() is not None: 
                raise Exception('unable to start')
        except Exception as e:
            self.shutdown()
            raise e
        
    def shutdown(self):
        # Read output until process closes

        try:
            # We write the command by hand here because if we call the cmd function
            # above we could end up in an infinite loop on shutdown
            self.agent.stdin.write(json.dumps({"cmd":"shutdown"}))
            self.agent.stdin.write("\n")
            self.agent.stdin.flush()

            self.agent.communicate(timeout=SHUTDOWN_TIMEOUT_SECONDS)
        except Exception as e:
            pass
        finally:
            try:
                os.kill(self.agent.pid, signal.SIGTERM)
            except Exception as e:
                pass
            self.agent = None

    def ensure_is_running(self):
        # Is the agent started?
        if not self.agent:
            self.startup()
        
        # is the agent still running?
        elif self.agent.poll() is None:
            # check for closed Pipes
            if self.agent.stdout.closed or self.agent.stdin.closed:
                self.startup()
            else:
                return True
        else:
            self.startup()

    def run_command(self, command):
        try:
            self.agent.stdin.write(json.dumps(command))
            self.agent.stdin.write("\n")
            self.agent.stdin.flush()
        except Exception as e:
            # if we get an exception here, we cannot run any new commands
            self.shutdown()
            raise e


    def readjsonline(self):
        try:
            line = None

            if not self.agent.stdout.closed:
                q = select.poll()
                q.register(self.agent.stdout,select.POLLIN)

                if q.poll(READ_TIMEOUT_SECONDS * 1000):
                    line = json.loads(self.agent.stdout.readline())
                else:
                    raise Exception("Read Timeout")

            if not line:
                raise Exception("invalid read")

            if line['error'] != 0:
                raise Exception(line['result'])

            return line
        except Exception as e:
            self.errors += 1
            if self.errors > ERRORS_BEFORE_RESTART:
                self.shutdown() ## if we are in bad state we may need to restart...
            raise e

    @stopwatch
    def ping_mediator(self):
        self.run_command({"cmd":"ping_mediator"})

        line = self.readjsonline()

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

    @task(10)
    def ping_mediator(self):
        self.client.ensure_is_running()

        self.client.ping_mediator()

class MyUser(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"