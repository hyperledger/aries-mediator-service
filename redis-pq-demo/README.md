# Example run-time

This is a demo that builds and deploys an instance of acapy that is configured to act as a mediator, and use [REDIS](https://redis.com/) as a resilient method of managing acapy's event queue with [this plugin](https://github.com/bcgov/aries-acapy-plugin-redis-events). 

How to see a full fledged demo, and a set of agents using the mediator (with redis)  

To run a redis-cluster and acapy as a mediator with redis for the first time. use the following commands

```
git clone https://github.com/hyperledger/aries-mediator-service.git z
cd redis-pq-demo
cp .\.env.sample .\.env 
docker-compose -f docker-compose.redis.yml up -d
docker-compose up --build
```

## Example agents

If you want to run a set of agents using the mediator, consider the acapy playground demo. 

```
git clone https://github.com/hyperledger/aries-cloudagent-python.git
cd demo/playground
cp .env.sample .env
APP_NETWORK_NAME=redis-cluster docker-compose up
```

There is a python script provided that will connect all the playground's agents using the provided invitation. Retrieve the invitiation url from the start-up logs of the mediator, and use that for MEDIATOR_INVITATION_URL in the following commands. 

```
cd scripts
pip install -r requirements.txt
<edit the MEDIATOR_INVITATION_URL in mediator_ping_agents.py>
python ./mediator_ping_agents.py
```