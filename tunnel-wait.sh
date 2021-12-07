#!/bin/bash

TUNNEL_ENDPOINT=${TUNNEL_ENDPOINT:-http://tunnel:4040}

while [[ "$(curl -s -o /dev/null -w '%{http_code}' "${TUNNEL_ENDPOINT}/status")" != "200" ]]; do
    echo "Waiting for tunnel..."
    sleep 1
done
ACAPY_ENDPOINT=$(curl --silent "${TUNNEL_ENDPOINT}/start" | python -c "import sys, json; print(json.load(sys.stdin)['url'])")
echo "fetched end point [$ACAPY_ENDPOINT]"

export ACAPY_ENDPOINT="[$ACAPY_ENDPOINT, ${ACAPY_ENDPOINT/http/ws}]"
#export ACAPY_ENDPOINT="$ACAPY_ENDPOINT"
exec "$@"