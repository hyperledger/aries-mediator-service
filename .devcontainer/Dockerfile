FROM ghcr.io/findy-network/findy-base:indy-1.16.ubuntu-22.04 AS indy-base

ARG VARIANT="jammy"

FROM mcr.microsoft.com/devcontainers/base:jammy

RUN apt-get update && \
  apt-get install -y curl libsodium23 openssl libzmq5 git zsh python3 build-essential ca-certificates

COPY --from=indy-base /usr/include/indy /usr/include/indy
COPY --from=indy-base /usr/lib/libindy.a /usr/lib/libindy.a
COPY --from=indy-base /usr/lib/libindy.so /usr/lib/libindy.so
COPY --from=indy-base /usr/lib/libssl.so.1.1 /usr/lib/libssl.so.1.1
COPY --from=indy-base /usr/lib/libcrypto.so.1.1 /usr/lib/libcrypto.so.1.1

USER vscode

RUN curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash && \
  export NVM_DIR="$HOME/.nvm" && \
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
  nvm install v16 && \
  npm install yarn -g

