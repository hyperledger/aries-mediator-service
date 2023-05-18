# Example run-time

This is a library that builds and deploys an instance of acapy that is configured to act as a mediator, and use REDIS to as a resilient method of managing acapy's event queue. 

How to see a full fledged demo, running a local ledger, and a set of agents using the mediator (with redis)  

1. Run the [acapy playground demo](https://github.com/hyperledger/aries-cloudagent-python/tree/main/demo/playground)
1. Run the redis-cluster service from aath/services [in PR branch](https://github.com/hyperledger/aries-agent-test-harness/pull/680)
1. Run this configuration, `docker-compose up --build`
1. Set `MEDITATOR_INVITATION_URL` in [mediator_ping_agents.py](https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/playground/scripts/mediator_ping_agents.py) to the invitation url provided by the mediator on startup. and run this python script, `python ./mediator_ping_agents.py` 

`mediator_ping_agents.py` accepts the mediator invitation for all the agents and pings the connections. If this succeed, each agent in the playground will have an active connection the mediator defined here. 