# Setup and Run

You're not meant to run production work load with `ts-node` so this project tries to get you off on the right foot. It will use `gulp` to facilitate the build. Once installed via:

```console
npm i -g gulp
```

You can continue with the following steps:

Transpile the source code from TypeScript to JavaScript so it can be run directly with nodejs.

```console
npm run build
```

Build your docker image. This will copy in the source as needed and do a few other things. See the Dockerfile for more information.

```console
docker build . --tag afj-mediator
```

Next run your mediator.

```console
docker run -it --rm -p 3001:3001 afj-mediator
```

At this point you should have a running mediator in AFJ.
