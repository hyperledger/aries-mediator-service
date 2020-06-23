
# infra

Indicio-specific infrastructure deployment and management tooling.

## Configuration

When running the Docker container, the following environment variables must be specified:

- DEPLOYMENT_ENV
- HTTP_PORT
- WS_PORT
- HTTP_ENDPOINT
- WS_ENDPOINT
- AGENT_NAME

In addition, be sure to expose the ports above on the Docker host.

Here's an example showing how to run the container directly from the CLI in interactive mode:

```sh
export IMAGE_VER=0.0.1
export IMAGE_NAME_FQ=707906211298.dkr.ecr.us-east-2.amazonaws.com/indicio-tech/aries-mediator

docker run -it \
    -e DEPLOYMENT_ENV=PROD \
    -e AGENT_NAME=example \
    -e HTTP_ENDPOINT=https://example.com \
    -e WS_ENDPOINT=ws://example.com \
    -e HTTP_PORT=3000 \
    -e WS_PORT=3001 \
    -p 3000:3000 \
    -p 3001:3001 \
    $IMAGE_NAME_FQ:$IMAGE_VER
```

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

3. Build the image. Note that you will need to set the IMAGE_VER environment variable:

    ```sh
    cd mediator
    IMAGE_VER=0.1.0 ./deploy mediator build
    ```

   By default, `build-image.sh` tags the image with the test environment ECR domain, but this can be overridden by setting the `ECR_DOMAIN` environment variable.

4. Test the image.

5. Push the image to AWS Elastic Container Registry (ECR):

    ```sh
    IMAGE_VER=0.1.0 ./deploy mediator push
    ```

6. The image can now be deployed to AWS Elastic Container Services (ECS).
