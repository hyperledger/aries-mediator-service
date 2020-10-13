# =============================================================================
# System
# =============================================================================

ARG BASE_IMAGE
ARG IMAGE_VER_BASE

FROM $BASE_IMAGE:$IMAGE_VER_BASE

# =============================================================================
# App
# =============================================================================

# (JamesKEbert) NOTE: the changes present at this commit have been merged into ACA-Py and are available at version 0.5.4. We will continue to use this commit (https://github.com/Indicio-tech/aries-cloudagent-python@feature/mediate_forward) until the Aries-Acapy-Plugin-Toolbox and Aries-Toolbox are updated to support ACA-Py 0.5.4
RUN pip3 install --no-cache-dir git+https://github.com/Indicio-tech/aries-cloudagent-python@feature/mediate_forward#egg=aries-cloudagent

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
