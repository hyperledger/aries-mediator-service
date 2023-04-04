# TL;DR

This runs the [AFJ](https://github.com/hyperledger/aries-framework-javascript) in a containerized environment.

# Setup and Run

This repo comes with a [.devContainer](../.devcontainer) that will allow you to build and run AFJ based src. It's added because AFJ requires some Indy libraries that can be a hassle to build. All the steps below work from the devContainer. The resulting AFJ mediator image will be placed on your local machine - no inside the devContainer.

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

Next, you can open a new terminal window (not one inside of the devContainer) and run the mediator. The optional parameter `AGENT_ENDPOINTS` can be used to override `localhost` as the endpoint the agent uses in invitations. Replace `foo.com` below with a custom endpoint or remove it if you are using this locally:

```console
docker run -it --rm -e AGENT_ENDPOINTS="http://foo.com:3001,ws://foo.com:3001" -p 3001:3001 afj-mediator
```

At this point you should have a running mediator in AFJ. You need to ask it for an invitation before you can use it. If you supplied an override via `AGENT_ENDPOINTS` above use the domain or IP below in place of `localhost`:

```console
curl http://localhost:3001/invitation
```

**🧐 Pro Tip**

If you are trying to connect to the mediatory from a local container, such as the the devContainer, and the mediator is using `localhost` you will need to use `host.docker.internal:3001`:

```console
curl http://host.docker.internal:3001/invitation
```
