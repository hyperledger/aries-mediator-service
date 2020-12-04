
# Mediator


## Local Build Process

```
docker build -f Dockerfile.base --no-cache -t indicio-tech/aries-mediator-base .
```

```
docker build --no-cache --build-arg BASE_IMAGE=indicio-tech/aries-mediator-base --build-arg IMAGE_VER_BASE=latest -t indicio-tech/aries-mediator .
```

You can run the docker container like so.

```
sh
export IMAGE_VER=latest
export IMAGE_NAME_FQ=indicio-tech/aries-mediator

docker run -it \
    -e DEPLOYMENT_ENV=TEST \
    -e AGENT_NAME=mediator-test \
    -e WALLET_NAME=test-1 \
    -e HTTP_ENDPOINT=http://example.com:3007 \
    -e WS_ENDPOINT=ws://example.com:3008 \
    -e HTTP_PORT=3007 \
    -e WS_PORT=3008 \
    -e RDBMS_URL=localhost:5432 \
    -e RDBMS_AUTH='{"account":"postgres","password":"setectastronomy","admin_account":"postgres","admin_password":"setectastronomy"}' \
    \
    -p 3007:3007 \
    -p 3008:3008 \
    \
    $IMAGE_NAME_FQ:$IMAGE_VER
```

You can also run the docker container using docker-compose. You may want to modify some of the parameters in the docker-compose.yml, such as HTTP_ENDPOINT.

```
docker-compose up
```

You can also run the docker container with ngrok for testing purposes by running.

```
docker-compose -f docker-compose-ngrok.yml up
```

## Configuration

When running the Docker container, the following environment variables must be specified (see below for example values):

- `DEPLOYMENT_ENV`: May be one of *DEV*, *TEST*, or *PROD*. Currently only *TEST* is implemented.
- `HTTP_PORT`: The port that the mediator should listen on for HTTP connections.
- `WS_PORT`: The port that the mediator should listen on for WebSocket connections.
- `HTTP_ENDPOINT`: The URI that the mediator should advertise for client connections over HTTP; this may use a different port than specified for `HTTP_PORT` in the case that a proxy or load balancer is used in front of the mediator instance.
- `WS_ENDPOINT`: The URI that the mediator should advertise for client connections over HTTP; this may use a different port than specified for `WS_PORT` in the case that a proxy or load balancer is used in front of the mediator instance.
- `AGENT_NAME`: The advertised name of the mediator.
- `WALLET_NAME`: Name for the mediator's wallet. All wallets will use the same PostgreSQL instance but different tables.
- `RDBMS_URL`: Host and port for the PostgreSQL instance where the wallet data will be stored.
- `RDBMS_AUTH`: JSON string specifying the credentials to use when connecting to the database. As demonstrated below, two sets of credentials are specified; one for normal data access and storage, and an "admin" credential that is used to initialize a new wallet. Currently the "admin" credential is always required by ACA-Py even when the wallet already exists, but there is work in progress to remedy this in the upstream codebase.

Optional:

- GENESIS_URL (default: https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_sandbox_genesis)

In addition, be sure to expose the ports above on the Docker host.

Here's an example showing how to run the container directly from the CLI in interactive mode:

```sh
export IMAGE_VER=latest
export IMAGE_NAME_FQ=indicio-tech/aries-mediator

docker run -it \
    -e DEPLOYMENT_ENV=TEST \
    -e AGENT_NAME=mediator-test \
    -e WALLET_NAME=test-1 \
    -e HTTP_ENDPOINT=http://example.com:8000 \
    -e WS_ENDPOINT=ws://example.com:8080 \
    -e HTTP_PORT=8000 \
    -e WS_PORT=8080 \
    -e RDBMS_URL=localhost:5432 \
    -e RDBMS_AUTH='{"account":"postgres","password":"setectastronomy","admin_account":"postgres","admin_password":"setectastronomy"}' \
    \
    -p 8000:8000 \
    -p 8080:8080 \
    \
    $IMAGE_NAME_FQ:$IMAGE_VER
```

## Debugging

When debugging an issue, you may wish to modify the app's logging level by editing `mediator/app/logging.ini`.
