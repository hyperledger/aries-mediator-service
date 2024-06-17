FROM ubuntu:24.04 as base

ARG LOADDIR="/load-agent"

## Using requirements from https://aries.js.org/guides/getting-started/installation/nodejs/linux

# Setup NodeJS environment for AFJ

ENV TZ=America/Denver
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update -y && apt-get install -y curl gcc g++ make git libssl-dev pkg-config

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get update -y && apt-get install -y nodejs

RUN npm install --global yarn

RUN apt-get install -y libsodium-dev libzmq3-dev

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rust.sh && sh -- rust.sh -y

RUN git clone https://github.com/hyperledger/indy-sdk

RUN cd indy-sdk/libindy && \
    /root/.cargo/bin/cargo build --release && \
    mv target/release/libindy.so /usr/lib/libindy.so

# Setup Locust

RUN apt-get install -y python3-pip

RUN pip3 install locust==2.14.2

FROM base as dev

# Setup Dev environment
RUN apt-get install -y tmux htop

# Include global arg in this stage of the build
ARG LOADDIR
# Set working directory to function root directory
WORKDIR ${LOADDIR}

FROM base as release

# Include global arg in this stage of the build
ARG LOADDIR
# Set working directory to function root directory
WORKDIR ${LOADDIR}

# TODO remove these changes when AFJ accepts merge
ADD ./aries-framework-javascript aries-framework-javascript

RUN cd aries-framework-javascript && yarn install

RUN cd aries-framework-javascript/packages/core && yarn install && npm run build

RUN cd aries-framework-javascript/packages/node && yarn install && npm run build

ADD ./load-agent load-agent

WORKDIR ${LOADDIR}/load-agent

RUN yarn install

CMD "locust"
