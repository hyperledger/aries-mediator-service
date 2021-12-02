# Aries Mediator Service

This repository provides a simple process for a developer to run an Aries mediator agent (currently based on Aca-py).

## Local Build Process

You can run the docker container like so.

```sh
git clone https://github.com/ianco/infra-mediator.git
cd infra-mediator
git checkout mediator_refactor
git submodule init
git submodule update
./manage build
./manage start --logs
```

The mediator-specific configuration parameters are in [./acapy/configs/mediator.yml](./acapy/configs/mediator.yml).

Other Aca-py parameters are specified by environment variables, set in the `./manage` script.

Note that this scenario starts an ngrok service to expose the Aca-py mediator's endpoint publicly.

## Running on Play With Docker (PWD) or Play With VON (PWV)

In a browser, connect to [PWD](https://labs.play-with-docker.com) or [PWV](http://play-with-von.vonx.io).

Then run the same commands as above:

```sh
git clone https://github.com/ianco/infra-mediator.git
cd infra-mediator
git checkout mediator_refactor
git submodule init
git submodule update
./manage build
./manage start --logs
```

Note that the `./manage` scripts auto-detects the PWD or PWV environment and sets the mediator endpoint appropriately (an ngrok service is not needed).

## Mediator Demo Controller

In the above example(s), the mediator agent is started in `--auto` mode, in that the agent will automatically accept connection requests.

This responsibility can be delegated to a [controller process](./acapy/controller), if some business rules (or human intervention) is required to approve connection requests.

To build/start this mediator process, run (assuming you are in the project directory):

```sh
./manage build --controller
./manage start --logs --controller
```


# === Old Docs ===

Old docs to be updated ...

## Local Build Process

You can run the docker container like so.

```sh
docker build -f Dockerfile --no-cache -t indicio-tech/aries-mediator .
docker run -it \
	-e ACAPY_ENDPOINT=["http://localhost:3000","ws://localhost:3000"] \
	-e ACAPY_WALLET_STORAGE_CONFIG={"url":"db:5432","wallet_scheme":"DatabasePerWallet"} \
	-e ACAPY_WALLET_STORAGE_CREDS={"account":"development","password":"development","admin_account":"development","admin_password":"development"} \
	-e ACAPY_WALLET_KEY=testing \
    \
    -p 3000:3000 \
    \
	indicio-tech/aries-mediator
```

You can also run the docker container by running. You may want to modify some of the parameters in the docker-compose.yml, such as HTTP_ENDPOINT.

```
docker-compose up
```

You can also run the docker container with ngrok for testing purposes by running.

```
docker-compose -f docker-compose-ngrok.yml up
```

# TODO Fix amazon builds

## Configuration

When running the Docker container, the following environment variables must be specified (see below for example values):

- `ACAPY_ENDPOINT`: Specify endpoint of mediator. Use `["http://localhost:3000","ws://localhost:3000"]` style syntax to specify multiple.
- `ACAPY_WALLET_STORAGE_COFNIG`: This will look something like: `{"url":"db:5432","wallet_scheme":"DatabasePerWallet"}`
- `ACAPY_WALLET_STORAGE_CREDS`: This will look something like: `{"account":"development","password":"development","admin_account":"development","admin_password":"development"}`
- `ACAPY_WALLET_KEY`: The key used to unlock the wallet.

More options may be specified as environment variables. See `aca-py start
--help` for more details on what environment variables are available.


Here's an example showing how to run the container directly from the CLI in interactive mode:

```sh
export IMAGE_VER=0.0.1
export IMAGE_NAME_FQ=707906211298.dkr.ecr.us-east-2.amazonaws.com/indicio-tech/aries-mediator

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

## Boostrapping

The first time a container runs with a new wallet, it will create a database in PostgreSQL for that wallet and initialize the wallet state. ACA-Py will output an invitiation that can be retrieved from the logs as needed:

https://us-east-2.console.aws.amazon.com/cloudwatch/home?region=us-east-2#logsV2:log-groups/log-group/$252Fecs$252Fmediator-test

In order to create the database, an admin account account and password must be provided in `RDBMS_AUTH`. Thereafter, this admin account should not be necessary and should be removed from the task definition.

For the production environment, additional controls will be put in place to secure the wallet and postgres credentials. (TBD)

## Building

The ECR domain that we use for our test environment is:

`707906211298.dkr.ecr.us-east-2.amazonaws.com`

1. Ensure Docker and the AWS CLI are installed. See also: [Getting Started with Amazon ECR](http://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html). You can use
a separate profile for the indicio-tech account by creating a directory for the same and
then setting the `AWS_SHARED_CREDENTIALS_FILE` and `AWS_CONFIG_FILE` environment variables (see
also: [Configuration and Credential File Settings](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)):

    ```sh
    mkdir .aws
    export AWS_CONFIG_FILE=$(pwd)/.aws/config
    export AWS_SHARED_CREDENTIALS_FILE=$(pwd)/.aws/credentials
    aws configure
    ```

2. Retrieve an authentication token and authenticate your Docker client to your registry:

    ```sh
    aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 707906211298.dkr.ecr.us-east-2.amazonaws.com
    ```

3. Build the image. Note that you will need to set the IMAGE_VER and IMAGE_VER_BASE environment variables:

    ```sh
    cd mediator
    IMAGE_VER=0.2.0 DEPLOYMENT_ENV=TEST ./deploy build mediator
    ```

   By default, `deploy` tags the image with the test environment ECR domain, but this can be overridden by setting the `ECR_DOMAIN` environment variable.

4. Test the image.

5. Push the image to AWS Elastic Container Registry (ECR):

    ```sh
    IMAGE_VER=0.2.0 DEPLOYMENT_ENV=TEST ./deploy push mediator
    ```

6. The image can now be deployed to AWS Elastic Container Services (ECS).

## Deploying

The Indicio test environment consists of an AWS ECS cluster and task definitions, a VPC, security groups, and an RDS postgres instance.

Resources are all located in the us-east-2 (Ohio) region:

* ECS Cluser: https://us-east-2.console.aws.amazon.com/ecs/home?region=us-east-2#/clusters/mediator-test/services
* Task Definition: https://us-east-2.console.aws.amazon.com/ecs/home?region=us-east-2#/taskDefinitions/mediator-test/status/ACTIVE
* RDS Instance: https://us-east-2.console.aws.amazon.com/rds/home?region=us-east-2#database:id=pg-mediator-test;is-cluster=false
* VPC: `vpc-0adb1b91d540e6bdc`
* Security Groups:
    * PostgreSQL: https://us-east-2.console.aws.amazon.com/vpc/home?region=us-east-2#SecurityGroup:groupId=sg-09cca4df418dfa271
    * Mediator: https://us-east-2.console.aws.amazon.com/vpc/home?region=us-east-2#SecurityGroup:groupId=sg-0505c4b8b008da4db
* Logs: https://us-east-2.console.aws.amazon.com/cloudwatch/home?region=us-east-2#logsV2:log-groups/log-group/$252Fecs$252Fmediator-test

To configure the mediator:

1. Go to the `Task Definitions` page in the Amazon ECS console for the us-east2 (Ohio) region.
2. Select the task definition to edit (e.g., `mediator-test`).
3. Under `Container Definitions` click on the container name.
4. Under `Environment` edit the environment variables as needed.

To launch a new task:

1. Go to the `mediator-test` cluster page in the Amazon ECS console for the us-east-2 (Ohio) region.
2. Select the `Tasks` tab and click `Run new Task`.
3. Choose the FARGATE launch type.
4. Choose `vpc-0adb1b91d540e6bdc` as the cluster VPC.
5. Choose one or both of the subnets for the cluster VPC.
6. Edit the security group and choose `sg-0505c4b8b008da4db`.
7. Chose `ENABLED` for the public IP auto-assignment. Fargate does not currently support elastic IPs directly; if necessary, an Application Load Balancer can be used to front the mediator instance and provide a stable IP address.
8. If accessing the instance directly, add/update the DNS record for the instance in Route53.
9. Retrieve the invitiation URL from CloudWatch Logs as needed.

## Debugging

When debugging an issue, you may wish to modify the app's logging level by editing `mediator/app/logging.ini`.
