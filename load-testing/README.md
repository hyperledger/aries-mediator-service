
## Setup VM to run 

```
apt-get update -y
apt-get upgrade -y
apt-get install -y docker.io git tmux htop sysstat iftop tcpdump
curl -SL https://github.com/docker/compose/releases/download/v2.7.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod a+x /usr/local/bin/docker-compose
 
cat << EOF > /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {"max-size": "10m", "max-file": "3"}
}
EOF
 
# Add swap file to add reliability to memory management...
dd if=/dev/zero of=/swap bs=1M count=512
chmod 0600 /swap
mkswap /swap
cat << EOF >> /etc/fstab
# add
/swap swap      swap    defaults        0 2
EOF

reboot
```

## Running load tests
```
git clone git@github.com:Indicio-tech/afj-load.git
cd afj-load
git clone git@github.com:reflectivedevelopment/aries-framework-javascript.git
cd aries-framework-javascript
git checkout feature/add_trustping_events
cd ..

# modify environment variables in docker-compose.yml to specify load test parameters
# MEDIATION_URL= add your mediation url here
# LOCUST_MIN_WAIT=60 min time between pings
# LOCUST_MAX_WAIT=120 max time between pings

docker-compose build
docker-compose up

# open web browser to localhost:8089
# run tests
```

## Load Test Notes

The start rate for clients, when to high will, will cause the mediator to be overloaded. 
Starting at new clients of 0.4 for every second is a good starting point.

Since the load testing uses AFJ for the clients, it may require more resources to run the
load environment than other Locust based load testing frameworks.

## Multi machine load test

Multiple locust nodes can be run to distribute the load testing. In the case of running
multiple nodes, you need to ensure each node has the environment variables set.

The master node will need to have a port opened to listen to incoming workers.

```
locust --master -P 8090
locust --worker
locust --worker  --master-host 10.128.15.214
```

## locustfile.py

The locustfile.py controls the AFJ agent by sending commands via STDIN and STDOUT over the subprocess.

This is done for two reasons.

- The ARIES Framework clients are known to throw uncaught exceptions or crash under some circumstances, such as timeouts
- AFJ is written in JavaScript, and does not have a Python integration at this time. Using a subprocess allows locust to call AFJ code.

There is some issues that arise from agents crashing. The locustfile code focuses on handling agent crashes and ensuring the agents are running
for the ping requests.

## agent.js

The agent.js is an event based architecture. It has a readline loop that listens for incoming commands. Commands are json strings. Examples

```
{"cmd":"start"}
{"cmd":"ping_mediator"}
{"cmd":"shutdown"}
```
