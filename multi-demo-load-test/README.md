# Multi-demo Mediator Load Test

This is a different set of load tests using an instance of Aca-Py in multitenant mode (`multi-demo`). This does not use AFJ to spawn agents, rather it will create agent/wallets in Aca-py and connect those agents to the mediator service.

**NOTE** This is a very early work in progress, the actual locust tests require significant tweaking, particularly around asking the mediator to mediate connections between other agents. Currently the agents are created and connected to the mediator service and each other, but  are not asking the mediator to mediate those connections... Coming soon!

## Dependencies

There are a lot of infrastructure to stand up. We will make use of existing docker-compose files.

1. ELK Stack for tracing mediator service and multi-demo.
2. Multi-demo
3. Mediator Service

For each of these, you will want to read their respective readmes and ensure that you can stand them up with agent tracing.

### ELK Stack

Currently in [PR 2216](https://github.com/hyperledger/aries-cloudagent-python/pull/2216), see demo/elk-stack.

Check out the above code, open a terminal and navigate to `demo/elk-stack`:

```
cp .env.sample .env
docker compose build
docker compose up
```

You will now have a docker network named `elknet` with elasticsearch, kibana, and logstash.  

Agent tracing for mediator and multi-demo will push to logstash at http://logstash:9700
Kibana can be accessed through browser at http://localhost:5601 using `elastic` / `changeme` for username and password. 

More to come later on setting up a useful search and dashboard. For now, useful fields for `Discover` are: traced_type, handler, ellapsed_milli, outcome, thread_id, msg_id

### Multi-demo

Multi-demo is also an Aca-Py demo project, so from the same source code, open a new terminal and navigate to `demo/multi-demo`.


First, change the docker-compose.yml file to run without `ngrok` tunneling and to push trace events to ELK. Edit `multi-agent` service to look like:

```
    environment:
      - NGROK_NAME=ngrok-agent
      - ACAPY_AGENT_ACCESS=${ACAPY_AGENT_ACCESS:-local}
      - ACAPY_ENDPOINT=http://multi-agent:8001
      - ACAPY_TRACE=${ACAPY_TRACE:-1}
      - ACAPY_TRACE_TARGET=${ACAPY_TRACE_TARGET:-http://logstash:9700/}
      - ACAPY_TRACE_TAG=${ACAPY_TRACE_TAG:-acapy.events}
      - ACAPY_TRACE_LABEL=${ACAPY_TRACE_LABEL:-multi.agent.trace}
      - ACAPY_AUTO_ACCEPT_INVITES=true
```

**NOTE** the change for `ACAPY_AGENT_ACCESS` from `public` to `local` - that turns off the `ngrok` tunneling.

Now, in our new terminal window, build and run `multi-demo`:

```
docker compose build
docker compose up
```

### Mediator Service

Now we add the mediator service with configuration to push tracing into ELK.

In yet another terminal, navigate to the root of this repository. The [docker-compose.multi-demo.yml](../docker-compose.multi-demo.yml) file is configured to work with the above ELK stack and multi-demo.

```
cp .env.multi-demo.sample .env
docker compose build
docker compose up
```

**NOTE** when the mediator service starts it will print an invitation url to the terminal - copy that value as you will need it for the load test. Be aware that this url will change each time the mediator is brought up.

Now we have two Aca-Py agents (`multi-demo` and `mediator`) adding tracing events through logstash into elasticsearch. Each agent has a different trace label (`multi.agent.trace` and `mediator.trace` respectively) so we can gather stats from each perspective.

### Load Test

Ok, so all the infrastucture is in place, now we can run our load test against the `mediator service` using `multi-demo` as our platform to increase agent load.  

Keep in mind, with all the docker containers, this is resource intensive (test machine provided docker with 16GB ram and 4 CPU). Mostly there are spikes when adding load, so we've set a [custom load shape](https://docs.locust.io/en/stable/custom-load-shape.html) to ramp up. With default configuration, we add 10 users (Aca-Py agents) per step, each step is 30 seconds and we want 50% of our users (agents) in use per second. The test runs for 10 minutes and will use a maximum of 100 users (agents). See  `.env.sample` for environment variables to change if you want to alter the load shape.

In another terminal, in this repo, in this directory (`multi-demo-load-test`):

```shell
cp .env.sample .env
<Copy invitation url from mediator service console and paste to .env MEDIATOR_INVITATION_URL>
docker compose build
docker compose up --scale workerlocust=4
```

**NOTE** the `--scale workerlocust=4` is simply an example of using locust's [distributed load](https://docs.locust.io/en/stable/running-distributed.html)

In browser, navigate to http://localhost:8089/#

We use a custom load shape (configured in .env), so no selection for Number of Users or Spawn Rate. The Host is set to hit the [multi-demo Aca-Py instance](http://multi-agent:8010).

Start swarming...

