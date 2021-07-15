FROM bcgovimages/aries-cloudagent:py36-1.16-0_0.6.0

RUN pip3 install --no-cache-dir git+https://github.com/hyperledger/aries-acapy-plugin-toolbox@v0.1.0

COPY ./configs configs

ENTRYPOINT ["/bin/sh", "-c", "\"$@\"", "--"]
CMD ["aca-py", "start", "--arg-file", "./configs/start.yml"]
