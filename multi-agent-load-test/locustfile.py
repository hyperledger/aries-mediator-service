import math

import logging
import uuid
import base64


from locust import (
    HttpUser,
    task,
    between,
    SequentialTaskSet,
    LoadTestShape,
    events,
)

from locust.runners import MasterRunner, WorkerRunner
from random_word import RandomWords

import config
import db

r = RandomWords()


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    # if not isinstance(environment.runner, MasterRunner):
    #     logging.debug("on_locust_init - Worker")
    if not isinstance(environment.runner, WorkerRunner):
        logging.debug("on_locust_init - Master")
        config.print_config()
        db.init()
        db.fetchall()


@events.quitting.add_listener
def on_locust_quitting(environment, **_kwargs):
    # if not isinstance(environment.runner, MasterRunner):
    #     logging.debug("on_locust_quitting - Worker")
    if not isinstance(environment.runner, WorkerRunner):
        logging.debug("on_locust_quitting - Master")
        db.close()


@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    # if not isinstance(environment.runner, MasterRunner):
    #     logging.debug(f"on_test_start(Worker): {_kwargs}")
    if not isinstance(environment.runner, WorkerRunner):
        logging.debug(f"on_test_start(Master): {_kwargs}")


class ConnectionData:
    connection_id: str
    alias: str
    state: str


class AcapyTenant(HttpUser):
    wait_time = between(2, 5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.wallet_id = None
        self.headers = None
        self.wallet_name = r.get_random_word()
        self.wallet_key = str(uuid.uuid4())
        # booleans to help flow...
        self.has_wallet = False
        # row id in wallets table
        self.row_id = None
        # mediator and at least another agent...
        self.connections = {}

    def on_start(self):
        if not self.has_wallet:
            logging.debug(f"> AcapyTenant.on_start({self.wallet_name})")
            # need to create the tenant and get the token
            data = {
                "key_management_mode": "managed",
                "wallet_dispatch_type": "default",
                "wallet_name": self.wallet_name,
                "wallet_key": self.wallet_key,
                "label": self.wallet_name,
                "wallet_type": "askar",
                "wallet_webhook_urls": [],
            }
            # playground multi-agent has no security for base wallet, just call multitenancy/wallet
            # to create a new tenant
            response = self.client.post(
                "/multitenancy/wallet", name="000_create_wallet", json=data
            )
            logging.debug(f"response = {response}")
            json = response.json()
            logging.debug(f"json = {json}")
            self.wallet_id = json["wallet_id"]
            self.token = json["token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.has_wallet = True
            self.row_id = db.add(self)
            logging.debug(f"< AcapyTenant.on_start({self.row_id}, {self.wallet_name})")

    @task
    class TopLevelTaskSet(SequentialTaskSet):
        @task
        class ConnectTaskSet(SequentialTaskSet):
            @task
            def connect_to_mediator(self):
                mediator = self.user.connections.get("mediator")
                if self.user.has_wallet and not mediator:
                    logging.debug(f"connect_to_mediator({self.user.wallet_name})")
                    _url = config.mediator_invitation_url
                    base64_message = _url.split("=", maxsplit=1)[1]
                    base64_bytes = base64_message.encode("ascii")
                    message_bytes = base64.b64decode(base64_bytes)
                    data = message_bytes.decode("ascii")
                    logging.debug(f"invitation_block = {data}")
                    params = {
                        "alias": "mediator",
                        "auto_accept": "true",
                    }
                    response = self.user.client.post(
                        "/connections/receive-invitation",
                        name="001_connect_to_mediator",
                        headers=self.user.headers,
                        params=params,
                        json=data,
                    )
                    logging.debug(f"response = {response}")
                    json = response.json()
                    logging.debug(f"json = {json}")
                    self.user.connections["mediator"] = json

            @task
            def stop(self):
                self.interrupt()

        @task
        def connections_list(self):
            logging.debug(f"list_connections({self.user.wallet_name})")
            response = self.user.client.get(
                "/connections", name="002_connections_list", headers=self.user.headers
            )
            logging.debug(f"response = {response}")
            json = response.json()
            logging.debug(f"json = {json}")
            # update our connections in memory (for pings etc)
            for row in json["results"]:
                self.user.connections[row["alias"]] = row

            for key in self.user.connections.keys():
                x = self.user.connections[key]
                logging.debug(
                    f"{self.user.wallet_name}: {x['alias']} ({x['their_role']}) = {x['state']}"
                )

        @task
        def connect_to_other(self):
            # if we are an even number in the created wallets/users
            # we are going to invite the previously created wallet/user to connect
            if (int(self.user.row_id) % 2) == 0:
                other = db.fetch_previous(self.user.row_id)
                # do we already have a connection?
                existing = self.user.connections.get(other["wallet_name"])
                if not existing:
                    # we need to create an invitation and they need to receive it
                    data = {"my_label": self.user.wallet_name}
                    params = {
                        "alias": other["wallet_name"],
                        "auto_accept": "true",
                    }
                    response = self.user.client.post(
                        "/connections/create-invitation",
                        name="011_create_invitation",
                        headers=self.user.headers,
                        params=params,
                        json=data,
                    )
                    logging.debug(f"response = {response}")
                    json = response.json()
                    logging.debug(f"json = {json}")
                    invitation = json["invitation"]
                    # set this, we will need it
                    connection_id = json["connection_id"]

                    data = invitation
                    params = {
                        "alias": self.user.wallet_name,
                        "auto_accept": "true",
                    }
                    response = self.user.client.post(
                        "/connections/receive-invitation",
                        name="012_receive_invitation",
                        headers={"Authorization": f"Bearer {other['token']}"},
                        json=data,
                        params=params,
                    )
                    logging.debug(f"response = {response}")
                    json = response.json()
                    logging.debug(f"json = {json}")
                else:
                    connection_id = existing["connection_id"]

                # ok, refresh the connection and add it to the user's connection dict
                response = self.user.client.get(
                    f"/connections/{connection_id}",
                    name="013_connection_fetch",
                    headers=self.user.headers,
                )
                logging.debug(f"response = {response}")
                json = response.json()
                logging.debug(f"json = {json}")
                self.user.connections[other["wallet_name"]] = json

        @task
        def ping_others(self):
            for key in self.user.connections.keys():
                test_name = "021_ping_mediator" if key == "mediator" else "022_ping_other"
                conn = self.user.connections[key]
                if conn["state"] == "active":
                    data = {"comment": f"{self.user.wallet_name} pinging..."}
                    response = self.user.client.post(
                        f"/connections/{conn['connection_id']}/send-ping",
                        name=test_name,
                        headers=self.user.headers,
                        json=data,
                    )
                    logging.debug(f"response = {response}")

class StepLoadShape(LoadTestShape):
    """
    A step load shape


    Keyword arguments:

        step_time -- Time between steps
        step_load -- User increase amount at each step
        spawn_rate -- Users to stop/start per second at every step
        time_limit -- Time limit in seconds

    """

    step_time = config.step_time
    step_load = config.step_load
    spawn_rate = config.spawn_rate
    time_limit = config.time_limit

    def tick(self):
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        current_step = math.floor(run_time / self.step_time) + 1
        return (current_step * self.step_load, self.spawn_rate)

