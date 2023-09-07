FROM ghcr.io/hyperledger/aries-cloudagent-python:py3.9-0.8.1

USER root
# install redis PQ acapy plugin
RUN pip install git+https://github.com/bcgov/aries-acapy-plugin-redis-events.git

USER $user

ADD https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 /usr/bin/jq
RUN chmod +x /usr/bin/jq

COPY ./start.sh start.sh
COPY ./configs configs

RUN chmod +x start.sh && \
  aca-py --version > ./acapy-version.txt

ENTRYPOINT ["bash", "./start.sh"]