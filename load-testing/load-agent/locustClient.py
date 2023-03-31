from locust import events
import time
import inspect
import json

import fcntl
import os
import requests
import signal

from gevent import subprocess
from gevent import select
from gevent import lock as gevent_lock

SHUTDOWN_TIMEOUT_SECONDS=10
READ_TIMEOUT_SECONDS=120
ERRORS_BEFORE_RESTART=10
START_PORT= json.loads(os.getenv('START_PORT'))
END_PORT= json.loads(os.getenv('END_PORT'))
class PortManager:
    def __init__(self):
        self.lock = gevent_lock.BoundedSemaphore()
        self.ports = list(range(START_PORT,END_PORT))

    def getPort(self):
        self.lock.acquire()
        try:
            port = self.ports.pop(0)
            return port
        finally:
            self.lock.release()

    def returnPort(self, port):
        self.lock.acquire()
        try:
            self.ports.append(port)
        finally:
            self.lock.release()

portmanager = PortManager()

def stopwatch(func):
    def wrapper(*args, **kwargs):
        # get task's function name
        previous_frame = inspect.currentframe().f_back
        file_name, _, task_name, _, _ = inspect.getframeinfo(previous_frame)

        start = time.time()
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            total = int((time.time() - start) * 1000)
            events.request_failure.fire(request_type="TYPE",
                                        name=file_name + '_' + task_name,
                                        response_time=total,
                                        exception=e,
                                        response_length=0)
        else:
            total = int((time.time() - start) * 1000)
            events.request_success.fire(request_type="TYPE",
                                        name=file_name + '_' + task_name,
                                        response_time=total,
                                        response_length=0)
        return result

    return wrapper

class CustomClient:
    def __init__(self, host):
        self.host = host
        self.agent = None
        self.errors = 0
        self.port = None
        self.withMediation = None

    _locust_environment = None

    @stopwatch
    def startup(self, withMediation=True):
        if (not self.withMediation) and self.withMediation is None:
            self.withMediation = withMediation
        try:
            if self.port is not None:
                portmanager.returnPort(self.port)
                self.port = None
            self.port = portmanager.getPort()

            self.errors = 0
            self.agent = subprocess.Popen(['node', 'agent.js'], 
                bufsize=0,
                universal_newlines=True, 
                stdout=subprocess.PIPE, 
                stdin=subprocess.PIPE,
                shell=False)

            self.run_command({
                "cmd": "start", 
                "withMediation": self.withMediation,
                "port": self.port
            })

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
            if self.port:
                portmanager.returnPort(self.port)
                self.port = None

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

    def is_running(self):
        if self.agent:
            return True
        return False

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

    @stopwatch
    def issuer_getinvite(self):
        headers = json.loads(os.getenv('ISSUER_HEADERS'))
        headers['Content-Type'] = 'application/json'
        r = requests.post(
            os.getenv('ISSUER_URL') + '/connections/create-invitation?auto_accept=true', 
            json={ "metadata": {}, "my_label": "Test" },
            headers=headers
            )
        if r.status_code != 200:
            raise Exception(r.content)
            
        r = r.json()

        return r

    @stopwatch
    def issuer_getliveness(self):
        headers = json.loads(os.getenv('ISSUER_HEADERS'))
        headers['Content-Type'] = 'application/json'
        r = requests.get(
            os.getenv('ISSUER_URL') + '/status', 
            json={ "metadata": {}, "my_label": "Test" },
            headers=headers
            )
        if r.status_code != 200:
            raise Exception(r.content)

        r = r.json()

        return r

    @stopwatch
    def accept_invite(self, invite):
        self.run_command({"cmd":"receiveInvitation", "invitationUrl": invite})

        line = self.readjsonline()

        return line['connection']

    @stopwatch
    def receive_credential(self, connection_id):
        self.run_command({"cmd":"receiveCredential"})

        headers = json.loads(os.getenv('ISSUER_HEADERS'))
        headers['Content-Type'] = 'application/json'

        issuer_did = os.getenv('CRED_DEF').split(':')[0]
        schema_parts = os.getenv('SCHEMA').split(':')


        r = requests.post(
            os.getenv('ISSUER_URL') + '/issue-credential/send', 
            json={
                "auto_remove": True,
                "comment": "Performance Issuance",
                "connection_id": connection_id,
                "cred_def_id": os.getenv('CRED_DEF'),
                "credential_proposal": {
                    "@type": "issue-credential/1.0/credential-preview",
                    "attributes": json.loads(os.getenv('CRED_ATTR'))
                },
                "issuer_did": issuer_did,
                "schema_id":  os.getenv('SCHEMA'),
                "schema_issuer_did": schema_parts[0],
                "schema_name": schema_parts[2],
                "schema_version": schema_parts[3],
                "trace": True
            },
            headers=headers
            )
        if r.status_code != 200:
            raise Exception(r.content)
            
        r = r.json()

        line = self.readjsonline()

        return r

    @stopwatch
    def revoke_credential(self, credential):
        headers = json.loads(os.getenv('ISSUER_HEADERS'))
        headers['Content-Type'] = 'application/json'

        issuer_did = os.getenv('CRED_DEF').split(':')[0]
        schema_parts = os.getenv('SCHEMA').split(':')

        time.sleep(1)

        r = requests.post(
            os.getenv('ISSUER_URL') + '/revocation/revoke', 
            json={
                "comment": "load test",
                "connection_id": credential['connection_id'],
                "cred_ex_id": credential['credential_exchange_id'],
                "notify": True,
                "notify_version": "v1_0",
                "publish": True
            },
            headers=headers
            )
        if r.status_code != 200:
            raise Exception(r.content)

    @stopwatch
    def msg_client(self, connection_id):
        self.run_command({"cmd":"receiveMessage"})

        headers = json.loads(os.getenv('ISSUER_HEADERS'))
        headers['Content-Type'] = 'application/json'

        r = requests.post(
            os.getenv('ISSUER_URL') + '/connections/' + connection_id + '/send-message', 
            json={
                "content": "ping"
            },
            headers=headers
            )
        r = r.json()

        line = self.readjsonline()

        return line
