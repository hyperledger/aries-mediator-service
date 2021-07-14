# =============================================================================
# System
# =============================================================================

ARG BASE_IMAGE
ARG IMAGE_VER_BASE

FROM $BASE_IMAGE:$IMAGE_VER_BASE

# =============================================================================
# App
# =============================================================================

RUN pip3 install --no-cache-dir git+https://github.com/hyperledger/aries-cloudagent-python@b8f28dfe1b8b84f1fd5143bd5219c93b0913c3cc#egg=aries-cloudagent

RUN pip3 install --no-cache-dir git+https://github.com/hyperledger/aries-acapy-plugin-toolbox@acapy053

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
