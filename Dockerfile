FROM dbluhm/aries-cloudagent:405715d1

COPY ./configs configs

ENTRYPOINT ["/bin/sh", "-c", "\"$@\"", "--"]
CMD ["aca-py", "start", "--arg-file", "./configs/start.yml"]
