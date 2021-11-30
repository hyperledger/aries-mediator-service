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

    echo "fetched end point [$ACAPY_ENDPOINT]"
    export ACAPY_ENDPOINT="[$ACAPY_ENDPOINT, ${ACAPY_ENDPOINT/http/ws}]"
else
    export ACAPY_ENDPOINT=${MEDIATOR_ENDPOINT_URL}
fi

echo "Starting aca-py agent with endpoint [$ACAPY_ENDPOINT] ..."
exec ./wait-for-it/wait-for-it.sh ${POSTGRESQL_HOST}:${POSTGRESQL_PORT} -s -t 60 -- \
    aca-py start --auto-provision \
    --arg-file ./acapy/configs/mediator.yml \
    --label "${MEDIATOR_AGENT_LABEL}" \
    --endpoint ${ACAPY_ENDPOINT} \
    --inbound-transport http 0.0.0.0 ${MEDIATOR_AGENT_HTTP_IN_PORT} \
    --outbound-transport ws \
    --outbound-transport http \
    --wallet-type indy \
    --wallet-storage-type postgres_storage \
    --admin 0.0.0.0 ${MEDIATOR_AGENT_HTTP_ADMIN_PORT} \
    --${MEDIATOR_AGENT_ADMIN_MODE}
