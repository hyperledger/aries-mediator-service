#!/bin/bash

NGROK_NAME=${NGROK_WS:-ngrok}

echo "ngrok end point [$NGROK_NAME]"

ENDPOINT=null
while [ -z "$ENDPOINT" ] || [ "$ENDPOINT" = "null" ]
do
    echo "Fetching end point from ngrok service"
    ENDPOINT=$(curl --silent $NGROK_NAME:4040/api/tunnels | ./jq -r '.tunnels[0].public_url')

    if [ -z "$ENDPOINT" ] || [ "$ENDPOINT" = "null" ]; then
        echo "ngrok not ready, sleeping 5 seconds...."
        sleep 5
    fi
done

echo "fetched end point [$ENDPOINT]"

export WS_ENDPOINT=${ENDPOINT/http/ws}
exec "$@"
