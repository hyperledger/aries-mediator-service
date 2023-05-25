# Example run-time

This is a demo that builds and deploys an instance of acapy that is configured to act as a mediator, and use REDIS as a resilient method of managing acapy's event queue. 

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
APP_NETWORK_NAME=redis-cluster docker-compose up
```

Next you will need to provide the script the inviation url by setting `MEDITATOR_INVITATION_URL` in [mediator_ping_agents.py](https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/playground/scripts/mediator_ping_agents.py) to the invitation url provided by the mediator on startup. and run this python script.

```
python ./mediator_ping_agents.py
```