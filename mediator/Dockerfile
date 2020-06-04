FROM bcgovimages/aries-cloudagent:py36-1.14-1_0.5.1

USER root
RUN apt-get update -y
USER 1001

CMD ["start", "--inbound-transport", "http",  "0.0.0.0", "8000", "--outbound-transport", "http"]
