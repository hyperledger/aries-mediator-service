# TL;DR

This runs the [AFJ](https://github.com/hyperledger/aries-framework-javascript) in a containerized environment.

# Setup and Run

This repo comes with a [.devContainer](../.devcontainer) that will allow you to build and run AFJ based src. It's added because AFJ requries some Indy libraries that can be a hastel to build. All the steps below work from the devContainer. The resulting AFJ mediator image will be placed on your local machine - no inside the devcontainer.

You're not meant to run production work load with `ts-node` so this project tries to get you off on the right foot by using `gulp` to orcestrate the build, which will transpile `.ts` to `.js`.

## Build

Setup the project dependencies:

```console
yarn install
```

Transpile the source code from TypeScript to JavaScript so it can be run directly with nodejs:

```console
yarn run build
```

Build your docker image. This will copy in the source as needed and do a few other things. See the Dockerfile for more information.

```console
docker build . --tag afj-mediator
```

Next, you can open a new terminal window (not one inside of the devcontainer) and run the mediator. Replace `foo.com` below with `localhost` if you are using this locally or some sort of proxy like ngrok if you want external access:

```console
docker run -it --rm -e AGENT_ENDPOINTS="http://foo.com:3001,ws://foo.com:3001" -p 3001:3001 afj-mediator
```

At this point you should have a running mediator in AFJ.
