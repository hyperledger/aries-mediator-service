# =============================================================================
# System
# =============================================================================

ARG IMAGE_VER_BASE

FROM 707906211298.dkr.ecr.us-east-2.amazonaws.com/indicio-tech/aries-mediator-base:$IMAGE_VER_BASE

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

COPY --chown=$user startup.sh ./startup
COPY logging.ini ./logging.ini

USER $user
CMD ./startup
