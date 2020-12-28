# =============================================================================
# System
# =============================================================================

ARG BASE_IMAGE
ARG IMAGE_VER_BASE

FROM $BASE_IMAGE:$IMAGE_VER_BASE

# =============================================================================
# App
# =============================================================================

RUN pip3 install --no-cache-dir git+https://github.com/hyperledger/aries-cloudagent-python@244194e68330835e5e2e53cc6c2993899d2437fb#egg=aries-cloudagent

RUN pip3 install --no-cache-dir git+https://github.com/hyperledger/aries-acapy-plugin-toolbox@93a51dc73a24cd556fe4243a5c0ab3c33e4d671d

# =============================================================================
# Runner
# =============================================================================

ADD https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 ./jq
USER root
RUN chmod +x ./jq
USER $user

COPY --chown=$user startup.sh ./startup
COPY logging.ini ./logging.ini

USER $user
CMD ./startup
