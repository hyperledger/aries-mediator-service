#!/bin/bash

if [[ "${ENV}" == "local" ]]; then
    NGROK_NAME=${NGROK_NAME:-ngrok}
    echo "using ngrok end point [$NGROK_NAME]"

    ACAPY_ENDPOINT=null
    while [ -z "$ACAPY_ENDPOINT" ] || [ "$ACAPY_ENDPOINT" = "null" ]
    do
        echo "Fetching end point from ngrok service [$NGROK_NAME:4040/api/tunnels]"
        ACAPY_ENDPOINT=$(curl --silent "$NGROK_NAME:4040/api/tunnels" | ./jq -r '.tunnels[] | select(.proto=="https") | .public_url')

        if [ -z "$ACAPY_ENDPOINT" ] || [ "$ACAPY_ENDPOINT" = "null" ]; then
            echo "ngrok not ready, sleeping 5 seconds...."
            sleep 5
        fi
    done

    NGROK_WS_NAME=${NGROK_WS_NAME:-ngrok_ws}
    echo "using ngrok end point [$NGROK_WS_NAME]"

    ACAPY_WSENDPOINT=null
    while [ -z "$ACAPY_WSENDPOINT" ] || [ "$ACAPY_WSENDPOINT" = "null" ]
    do
        echo "Fetching end point from ngrok service [$NGROK_WS_NAME:4040/api/tunnels]"
        ACAPY_WSENDPOINT=$(curl --silent "$NGROK_WS_NAME:4040/api/tunnels" | ./jq -r '.tunnels[] | select(.proto=="https") | .public_url')

        if [ -z "$ACAPY_WSENDPOINT" ] || [ "$ACAPY_WSENDPOINT" = "null" ]; then
            echo "ngrok not ready, sleeping 5 seconds...."
            sleep 5
        fi
    done

    echo "fetched end point [$ACAPY_ENDPOINT]"
    echo "fetched ws end point [$ACAPY_WSENDPOINT]"
    ACAPY_ENDPOINT="[$ACAPY_ENDPOINT, ${ACAPY_WSENDPOINT/http/ws}]" 
    export ACAPY_ENDPOINT="$ACAPY_ENDPOINT"

elif [[ "${ENV}" == "local_tunnel" ]]; then
    TUNNEL_ENDPOINT=${TUNNEL_ENDPOINT:-http://tunnel:4040}

    while [[ "$(curl -s -o /dev/null -w '%{http_code}' "${TUNNEL_ENDPOINT}/status")" != "200" ]]; do
        echo "Waiting for tunnel..."
        sleep 1
    done
    ACAPY_ENDPOINT=$(curl --silent "${TUNNEL_ENDPOINT}/start" | python -c "import sys, json; print(json.load(sys.stdin)['url'])")
    echo "fetched end point [$ACAPY_ENDPOINT]"


    TUNNEL_WS_ENDPOINT=${TUNNEL_WS_ENDPOINT:-http://tunnel_ws:4040}

    while [[ "$(curl -s -o /dev/null -w '%{http_code}' "${TUNNEL_WS_ENDPOINT}/status")" != "200" ]]; do
        echo "Waiting for tunnel..."
        sleep 1
    done
    ACAPY_WSENDPOINT=$(curl --silent "${TUNNEL_WS_ENDPOINT}/start" | python -c "import sys, json; print(json.load(sys.stdin)['url'])")
    echo "fetched ws end point [$ACAPY_WSENDPOINT]"

    ACAPY_ENDPOINT="[$ACAPY_ENDPOINT, ${ACAPY_WSENDPOINT/http/ws}]"
    export ACAPY_ENDPOINT="$ACAPY_ENDPOINT"

else
    export ACAPY_ENDPOINT=${MEDIATOR_ENDPOINT_URL}
fi

echo "Starting aca-py agent with endpoint [$ACAPY_ENDPOINT] ..."
exec ./wait-for-it/wait-for-it.sh ${POSTGRESQL_HOST}:${POSTGRESQL_PORT} -s -t 60 -- \
    aca-py start --auto-provision \
    --arg-file ${MEDIATOR_ARG_FILE} \
    --label "${MEDIATOR_AGENT_LABEL}" \
    --inbound-transport http 0.0.0.0 ${MEDIATOR_AGENT_HTTP_IN_PORT} \
    --inbound-transport ws 0.0.0.0 ${MEDIATOR_AGENT_WS_IN_PORT} \
    --outbound-transport ws \
    --outbound-transport http \
    --wallet-type indy \
    --wallet-storage-type postgres_storage \
    --admin 0.0.0.0 ${MEDIATOR_AGENT_HTTP_ADMIN_PORT} \
    --${MEDIATOR_AGENT_ADMIN_MODE} \
    ${MEDIATOR_CONTROLLER_WEBHOOK}



