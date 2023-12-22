FROM ghcr.io/hyperledger/aries-cloudagent-python:py3.9-0.10.4

USER root
# Install redis PQ acapy plugin
RUN pip install git+https://github.com/hyperledger/aries-acapy-plugins.git@main#subdirectory=redis_events

USER $user

ADD https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 /usr/bin/jq
RUN chmod +x /usr/bin/jq

COPY ./start.sh start.sh
COPY ./configs configs

RUN chmod +x start.sh && \
  aca-py --version > ./acapy-version.txt

ENTRYPOINT ["bash", "./start.sh"]