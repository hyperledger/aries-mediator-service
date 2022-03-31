# Aries Mediator Service

## TL;DR

This repository provides a simple process for a developer to run an Aries mediator agent. You should be able to bring the stack on-line by copying `.env.stample` to `.env` and running `docker-compose up`. For more information, keep reading.

Special thanks to [Indicio](https://indicio.tech) 🙏 for their original contribution of this project.

## Build & Run 

This is setup to be run as is with a simple `docker-compose up`. When run it will fire up the following containers:

### ngrok

You need to accept inbound connections. Most of us are behind firewalls or have impermanent IP addresses. Ngrok is used as a proxy to work around this. It will provide the URL that will act as a front door for your wallet to access the mediator service.

If you have a paid ngrok account you can provide your access token as one of the parameters (via the .env file). If not, leave it blank and it'll assume your on the free plan.

Pro Tip 🤓 

- Free plans can only keep a connection open for 60 minutes. After this, you will need to restart the stack. If this gets annoying, use a paid plan for a long lived tunnel :)

- Every time your restart the stack (all the containers) the URL will change. You may be able to work around this with different paid plans.

### Caddy

Your wallet needs to open two connections to the mediator: The first is a standard **https** connection. This will be embedded in the invitation and will be used by the wallet for standard CRUD operations. Once the invite is accepted, a second WebSocket (wss) connection will be opened. This will be the primary mode of communication between the mediator and your wallet.

Caddy is used to route **http** and **wss** traffic to the correct transport on the mediator. Without it, two ngrok tunnels would need to be started making startup and configuration a little more complicated.

In any case, I think its more clear and consumable to have a single URL.

### Mediator Demo Controller

The mediator is configured to allow it to automatically accept connections. This functionality can be delegated to a controller process if business rules require approval / intervention before accepting a connection. A sample controller to do this is included with the project.

This custom **nodejs** app, written in TypeScript, uses [Feathers JS](https://feathersjs.com) to provide RESTFull endpoints to ACA-py. To enable the controller and have it determine if connections should be accepted:

1. Update the mediator configuration

In the `.env` file override the mediator config environment variable by adding `MEDIATOR_ARG_FILE` as follows:

```
MEDIATOR_ARG_FILE=./configs/mediator-with-controller.yml
```

2. Enable the mediator service in the docker stack 

Remove these two lines from the [docker-compose.yml](./docker-compose.yml) file in the `mediator-controller` service:

```
    profiles:
      - donotstart
```

3. Add the following line to [start.sh](./acapy/start.sh) to allow the mediator to find and use the controller:

```
    --webhook-url ${MEDIATOR_CONTROLLER_WEBHOOK}
```

### Mediator

A mediator is just a special type of agent. In this case, the mediator is ACA-py, with a few special config params, into make it run as a "mediator" rather than a traditional agent.

About 1/2 of the params for ACA-py are provided in `start.sh`, others are passed via a configuration file [mediator-auto-accept.yml](./acapy/configs/mediator.yml). Move them around as you see fit. Ones that are likely to change are better kept as environment variables.

### PostgreSQL

[PostgreSQL](https://www.postgresql.org) is well known RDBMS. It is used by the mediator persist wallet information. Without it, the wallet would be reset every time the stack is restarted. The first time the mediator container runs it will create a database for its wallet and initialize the wallet state.

### Run It !

0. Put some tunes on, it'll help. Here's one to get you started [Bossa Nova - Take On Me](https://open.spotify.com/track/7rpDM5zKuWaf2VzXFKU3yV?si=6aacebaa532d4848). You should have it up and running before the song is done.

1. Start by cloning this repo:

```console
git clone git@github.com:fullboar/aries-mediator-service.git
```

2. Copy the file `env.sample` to `.env` in the root of the project. The default values are fine, edit as you see fit. This file will be used by `docker-compose` to add or override any environment variables.

```console
cp env.sample .env
```

Pro Tip 🤓

You can generate strong tokens for production with `OpenSSL`:

```console
openssl rand 32 -hex
```

3. Bring up the stack. When you first run this command it will build the mediator container so it may take a few moments. Subsequent restarts will be much faster.

```console
docker-compose up
```

When the stack is on-line you'll see a big white QR code scroll up your screen, just above that is your invitation URL. I'll look something like this:

```console
mediator_1             | Invitation URL (Connections protocol):
mediator_1             | https://ed49-70-67-240-52.ngrok.io?c_i=eyJAdHlwZSI6ICJkaWQ6c292OkJ6Q2JzTlloTXJqSGlxWkRUVUFTSGc7c3BlYy9jb25uZWN0aW9ucy8xLjAvaW52aXRhdGlvbiIsICJAaWQiOiAiZmYwMjkzNmYtNzYzZC00N2JjLWE2ZmYtMmZjZmI2NmVjNTVmIiwgImxhYmVsIjogIk1lZGlhdG9yIiwgInJlY2lwaWVudEtleXMiOiBbIkFyVzd1NkgxQjRHTGdyRXpmUExQZERNUXlnaEhXZEJTb0d5amRCY0UzS0pEIl0sICJzZXJ2aWNlRW5kcG9pbnQiOiAiaHR0cHM6Ly9lZDQ5LTcwLTY3LTI0MC01Mi5uZ3Jvay5pbyJ9
```

The `c_i` parameter is your reusable invitation encoded as base64. Let's decode it and see what's inside:

```json
{"@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/invitation", "@id": "ff02936f-763d-47bc-a6ff-2fcfb66ec55f", "label": "Mediator", "recipientKeys": ["ArW7u6H1B4GLgrEzfPLPdDMQyghHWdBSoGyjdBcE3KJD"], "serviceEndpoint": "https://ed49-70-67-240-52.ngrok.io"}
```

Pro Tip 🤓

The invitation will be regenerated every time you restart the docker stack for two important reason:

1. The `ngrok` URL changes with restarts; and 
2. The database is not persistent. This is where wallet initialization data, like `verkey` is stored. This will cause the `@id` and `recipientKeys` properties to change in the invitation (`c_i` payload above).

The general workaround steps are: 

- expose the caddy ports outside of the container; 
- start `ngrok` outside of a container and update the MEDIATOR_URL in [start.sh](./acapy/start.sh);
- give postgres a persistent volume;

### Aries Bifold Wallet Integration

You can easily use your newly minted mediator with the [Aries Bifold wallet](https://github.com/hyperledger/aries-mobile-agent-react-native). Take the full invitation URL from above and provide it to Bifold through the `MEDIATOR_URL` parameter. This can be in the form of an environment variable or, a more reliable way is to create a `.env` file in the root of the project with the parameter `MEDIATOR_URL` in it like this:

```console
MEDIATOR_URL=https://ed49-70-67-240-52.ngrok.io?c_i=eyJAdHlwZSI6ICJkaWQ6c292OkJ6Q2JzTlloTXJqSGlxWkRUVUFTSGc7c3BlYy9jb25uZWN0aW9ucy8xLjAvaW52aXRhdGlvbiIsICJAaWQiOiAiZmYwMjkzNmYtNzYzZC00N2JjLWE2ZmYtMmZjZmI2NmVjNTVmIiwgImxhYmVsIjogIk1lZGlhdG9yIiwgInJlY2lwaWVudEtleXMiOiBbIkFyVzd1NkgxQjRHTGdyRXpmUExQZERNUXlnaEhXZEJTb0d5amRCY0UzS0pEIl0sICJzZXJ2aWNlRW5kcG9pbnQiOiAiaHR0cHM6Ly9lZDQ5LTcwLTY3LTI0MC01Mi5uZ3Jvay5pbyJ9
```

## FAQ

### How does Bifold talk to the Mediator?

I struggled quite a bit with how HTTP/s and WSS are managed internally. The key, for me, was the `--endpoint` argument in ACA-py. To run a mediator, and maybe other agents, it takes two params for this argument. The first is the HTTP/s endpoint and the second is the `WSS` endpoint.

The HTTP/s endpoints, as per the docs on this param, will be used for invitations. Its going to be how your wallet finds and opens a dialogue with the mediator. Once a connection is established the WSS endpoint will be how the mediator and your wallet primarily communicated; they will message over the WebSocket. 

### Can I use two URLs rather than one?

You can use two different URLs and route them to the respective ports on the mediator. It won't care. As per "How does Bifold talk to the Mediator" just make sure the HTTP/s port is the first in the `--endpoint` argument and use `wss://` ad the protocol in the second param even though the URL is the same.

I've used one URL and setup Caddy to route traffic to the correct port on the mediator. I think this setup is much more clear making it easier to consume and maintain.

### Are there other ways to manage transports?

Sure. There is a ACA-py plug-in that will allow it to take both HTTP/s and WSS traffic over a single port. You can find it in the [Plugin Toolbox](https://github.com/hyperledger/aries-acapy-plugin-toolbox)

My pro-tip is use Caddy. Reverse proxies are a tried and tru technology.

### Why Caddy?

I get asked a bit why Caddy? NGINX is great, but I find you need a PhD in NGINX to configure it. Caddy is lightweight and built from the ground up be more effective in cloud (k8s / OpenShift) deployments and has more human friendly config.
