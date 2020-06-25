#!/bin/bash

echo "Starting aca-py with:"
echo
echo "   DEPLOYMENT_ENV: $DEPLOYMENT_ENV"
echo "   HTTP_PORT: $HTTP_PORT"
echo "   WS_PORT: $WS_PORT"
echo "   HTTP_ENDPOINT: $HTTP_ENDPOINT"
echo "   WS_ENDPOINT: $WS_ENDPOINT"
echo "   AGENT_NAME: $AGENT_NAME"
echo


if [[ "$DEPLOYMENT_ENV" == "TEST" ]]; then

    aca-py start \
        -it http 0.0.0.0 $HTTP_PORT \
        -it ws 0.0.0.0 $WS_PORT \
        -ot http \
        -e "$HTTP_ENDPOINT" "${WS_ENDPOINT}" \
        --label "$AGENT_NAME" \
        --invite --invite-role admin --invite-label "$AGENT_NAME (admin)" \
        --genesis-url https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_sandbox_genesis \
        --wallet-type indy \
        --wallet-storage-config '{"path": "/etc/indy"}' \
        --wallet-name $DEPLOYMENT_ENV \
        --plugin acapy_plugin_toolbox

else

    echo "Only the TEST environment is currently supported (given: DEPLOYMENT_ENV=$DEPLOYMENT_ENV)"

fi
