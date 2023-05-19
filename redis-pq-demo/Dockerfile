FROM ghcr.io/hyperledger/aries-cloudagent-python:py3.9-0.8.1

USER root
# install redis PQ acapy plugin
RUN pip install git+https://github.com/bcgov/aries-acapy-plugin-redis-events.git

USER $user
COPY ./configs configs

CMD ["aca-py"] 