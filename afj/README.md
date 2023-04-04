# TL;DR

This runs the [AFJ](https://github.com/hyperledger/aries-framework-javascript) in a containerized environment.

# Setup and Run

This repository includes a [.devContainer](../.devcontainer) that enables you to build and run AFJ-based source code. This feature is provided because AFJ depends on certain Indy libraries that can be challenging to compile. All the procedures mentioned below can be executed within the devContainer. The resulting AFJ mediator image will be stored on your local machine, not inside the devContainer.

It is not recommended to use ts-node for running production workloads. Therefore, this project aims to start you off correctly by utilizing gulp for build orchestration. This will convert your .ts (TypeScript) files into .js (JavaScript) files.

## Build

Setup the project dependencies:

```console
yarn install
```

Transpile the source code from TypeScript to JavaScript, allowing it to be executed directly with Node.js:

```console
yarn run build
```

Build your docker image. This will copy in the source as needed and do a few other things. See the Dockerfile for more information.

```console
docker build . --tag afj-mediator
```

Next, open a new terminal window (not within the devContainer) to run the mediator. You can use the optional AGENT_ENDPOINTS parameter to replace localhost with a custom endpoint for the agent to use in invitations. Substitute foo.com with your desired endpoint or remove it altogether if you are using this locally:

```console
docker run -it --rm -e AGENT_ENDPOINTS="http://foo.com:3001,ws://foo.com:3001" -p 3001:3001 afj-mediator
```

By now, you should have a running mediator in AFJ. To use it, you must first request an invitation. If you provided a custom endpoint using the AGENT_ENDPOINTS parameter earlier, replace localhost with the corresponding domain or IP address:

```console
curl http://localhost:3001/invitation
```

**🧐 Pro Tip**

To connect to the mediator from a local container, such as the devContainer, when the mediator is using localhost, use the address `host.docker.internal:3001`:.

```console
curl http://host.docker.internal:3001/invitation
```
