# Example run-time

This is a demo that builds and deploys an instance of acapy that is configured to act as a mediator, and use [REDIS](https://redis.com/) as a resilient method of managing acapy's event queue with [this plugin](https://github.com/bcgov/aries-acapy-plugin-redis-events). 

How to see a full fledged demo, and a set of agents using the mediator (with redis)  

To run a redis-cluster and acapy as a mediator with redis for the first time. use the following commands

```
git clone https://github.com/hyperledger/aries-mediator-service.git
cd aries-mediator-service/redis-pq-demo
cp .env.sample .env 
docker-compose -f docker-compose.redis.yml up -d
docker-compose up --build
```

After establishing a connection with the mediator. You can inspect the contents of the redis cluster with the redis-ui container by going to `http://localhost:7843`, if you see any keys in the cluster, then it's connected properly!

## Example agents

If you want to run a set of agents using the mediator, consider the acapy [playground](https://github.com/hyperledger/aries-cloudagent-python/blob/8311adca7f69e6003b98af2d033b4e441611ecf5/demo/playground/README.md) demo. 

```
git clone https://github.com/hyperledger/aries-cloudagent-python.git
cd aries-cloudagent-python/demo/playground
cp .env.sample .env
APP_NETWORK_NAME=redis_cluster APP_NETWORK_EXTERNAL=true docker-compose up --build
```

Along with the playground, there are examples that illustrate connecting the playground agents through the mediator and pinging each other. Retrieve the invitiation url from the start-up logs of the mediator, and use that for MEDIATOR_INVITATION_URL in the following commands. 

```
<new terminal at aries-cloudagent-python/demo/playground>
cd examples
docker compose build
APP_NETWORK_NAME=redis_cluster docker compose run -e MEDIATOR_INVITATION_URL=<your mediator invitation url> tests -s
```
