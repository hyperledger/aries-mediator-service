# Multi-agent (Playground) Mediator Load Test

This is a different set of load tests using an instance of ACA-Py in multi-tenant mode (`multi-agent`). This does not use AFJ to spawn agents, rather it will create agent/wallets in ACA-Py and connect those agents to the mediator service.

## Dependencies

There is a lot of infrastructure to stand up. We will make use of existing docker-compose files.

1. ELK Stack for tracing mediator service and multi-agent.
2. Playground (multi-agent)
3. Mediator Service

For each of these, you will want to read their respective readmes and ensure that you can stand them up with agent tracing.

### ELK Stack

In [ACA-Py](https://github.com/hyperledger/aries-cloudagent-python), see [demo/elk-stack](https://github.com/hyperledger/aries-cloudagent-python/tree/1daba1873369963d245551423d4c7b6182173c51/demo/elk-stack).

Check out the above code, open a terminal and navigate to `demo/elk-stack`:

```shell
cp .env.sample .env
docker compose build
docker compose up
```

You will now have a docker network named `elknet` with elasticsearch, kibana, and logstash.  

Agent tracing for mediator and playground/multi-agent will push to logstash at http://logstash:9700
Kibana can be accessed through browser at http://localhost:5601 using `elastic` / `changeme` for username and password. 

More to come later on setting up a useful search and dashboard. For now, useful fields for `Discover` are: traced_type, str_time, handler, ellapsed_milli, outcome, thread_id, msg_id

### Playground / Multi-Agent

`playground` is also an ACA-Py demo project, so from the same source code, open a new terminal and navigate to `demo/playground`. It is advisable that you read through its `README`

`playground` can stand up 2 single-tenant agents and multi-tenant agent. For this, we will use the multi-tenant agent: `multi-agent`.

First you will need to create the default environment file, and we will make a few tweaks.

- turn off `ngrok` for `multi-agent`

```shell
cp .env.sample .env
```

In `.env`, change `MULTI_TUNNEL_NAME=multi` to `MULTI_TUNNEL_NAME=`. This will turn off `ngrok` for `multi-agent`. Ngrok will throw `429 - Too Many Requests` errors if we flood it in the load test.

- turn on tracing

Still in `.env`, change `ACAPY_TRACE=0` to `ACAPY_TRACE=1`. And in `docker-compose.yml`, uncomment the agent tracing section for `multi-agent` (ensure that the `elk-network` is uncommented too).

```shell
      - ACAPY_TRACE=${MULTI_ACAPY_TRACE}
      - ACAPY_TRACE_TARGET=${MULTI_ACAPY_TRACE_TARGET}
      - ACAPY_TRACE_TAG=${MULTI_ACAPY_TRACE_TAG}
      - ACAPY_TRACE_LABEL=${MULTI_ACAPY_TRACE_LABEL}
      ...
    networks:
      - app-network
      - elk-network
```

Now, in our new terminal window, build and run `playground / multi-agent`:

```
docker compose build
docker compose up multi-agent
```

### Mediator Service

Now we add the mediator service with configuration to push tracing into ELK.

In yet another terminal, navigate to the root of this repository. The [docker-compose.multi-agent.yml](../docker-compose.multi-agent.yml) file is configured to work with the above ELK stack and multi-agent.

```
cp .env.multi-agent.sample .env
docker compose -f docker-compose.multi-agent.yml build
docker compose -f docker-compose.multi-agent.yml up
```

**NOTE** when the mediator service starts it will print an invitation url to the terminal - copy that value as you will need it for the load test. Be aware that this url will change each time the mediator is brought up.

Now we have two ACA-Py agents (`multi-agent` and `mediator`) adding tracing events through logstash into elasticsearch. Each agent has a different trace label (`multi.agent.trace` and `mediator.trace` respectively) so we can gather stats from each perspective.

## Load Test

Ok, so all the infrastructure is in place, now we can run our load test against the `mediator service` using `multi-agent` as our platform to increase agent load.  

Keep in mind, with all the docker containers, this is resource intensive (test machine provided docker with 16GB ram and 4 CPU). Mostly there are spikes when adding load, so we've set a [custom load shape](https://docs.locust.io/en/stable/custom-load-shape.html) to ramp up. With default configuration, we add 10 users (Aca-Py agents) per step, each step is 30 seconds and we want 50% of our users (agents) in use per second. The test runs for 10 minutes and will use a maximum of 100 users (agents). See  `.env.sample` for environment variables to change if you want to alter the load shape.

In another terminal, in this repo, build/run the load test:

```shell
cd multi-agent-load-test
cp .env.sample .env
<Copy invitation url from mediator service console and paste to .env MEDIATOR_INVITATION_URL>
docker compose build
docker compose up --scale workerlocust=4
```

**NOTE** the `--scale workerlocust=4` is simply an example of using locust's [distributed load](https://docs.locust.io/en/stable/running-distributed.html)

In browser, navigate to http://localhost:8089/#

We use a custom load shape (configured in .env), so no selection for Number of Users or Spawn Rate. The Host is set to hit the [multi-agent ACA-Py instance](http://multi-agent:9014).

Start swarming...

## Networking

For running load tests locally, we do not want to use `ngrok`. If the steps above are followed, the `mediator` and `multi-agent` will be in the `elknet` network and `multi-agent` can resolve `mediator`. `multi-agent` and `multilocust`/`workerlocust` are in `playgroundnet` so locust containers can resolve `multi-agent`. If you want to run the load test with different infrastructure be aware of how they connect and resolve their hosts.  
