# =============================================================================
# System
# =============================================================================

ARG BASE_IMAGE
ARG IMAGE_VER_BASE

FROM $BASE_IMAGE:$IMAGE_VER_BASE

# =============================================================================
# App
# =============================================================================

RUN pip3 install --no-cache-dir git+https://github.com/Indicio-tech/aries-cloudagent-python@feature/mediate_forward#egg=aries-cloudagent

# TODO: Pin this to a specific commit/version
# https://github.com/Indicio-tech/aries-acapy-plugin-toolbox/tree/feature/routingadmin
RUN pip3 install --no-cache-dir git+https://github.com/Indicio-tech/aries-acapy-plugin-toolbox.git@feature/routingadmin#egg=aries-acapy-plugin-toolbox

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
