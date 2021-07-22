#!/bin/bash

NGROK_NAME=${NGROK_NAME:-ngrok}

echo "ngrok end point [$NGROK_NAME]"

ACAPY_ENDPOINT=null
while [ -z "$ACAPY_ENDPOINT" ] || [ "$ACAPY_ENDPOINT" = "null" ]
do
    echo "Fetching end point from ngrok service"
    ACAPY_ENDPOINT=$(curl --silent "$NGROK_NAME:4040/api/tunnels" | ./jq -r '.tunnels[0].public_url')

    if [ -z "$ACAPY_ENDPOINT" ] || [ "$ACAPY_ENDPOINT" = "null" ]; then
        echo "ngrok not ready, sleeping 5 seconds...."
        sleep 5
    fi
done

echo "fetched end point [$ACAPY_ENDPOINT]"

export ACAPY_ENDPOINT="[$ACAPY_ENDPOINT, ${ACAPY_ENDPOINT/http/ws}]"
exec "$@"
