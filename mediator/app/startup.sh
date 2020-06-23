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


if [[ "$DEPLOYMENT_ENV" == "PROD" ]]; then
    # TODO(kgriffs): Customize arguments for PROD env
    # TODO(kgriffs): How do we bootstrap the agent invitiation/connection
    #   programmatically (vs. copy-pasting from the console?)

    aca-py start \
        -it http 0.0.0.0 $HTTP_PORT \
        -it ws 0.0.0.0 $WS_PORT \
        -ot http \
        -e "$HTTP_ENDPOINT" "${WS_ENDPOINT}" \
        --label "$AGENT_NAME" \
        --auto-accept-requests --auto-ping-connection \
        --auto-respond-credential-proposal --auto-respond-credential-offer --auto-respond-credential-request --auto-store-credential \
        --auto-respond-presentation-proposal --auto-respond-presentation-request --auto-verify-presentation \
        --invite --invite-role admin --invite-label "$AGENT_NAME (admin)" \
        --genesis-url https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_sandbox_genesis \
        --wallet-type indy \
        --plugin acapy_plugin_toolbox \
        --debug-connections \
        --debug-credentials \
        --debug-presentations \
        --enable-undelivered-queue
else
    # TODO(kgriffs): Customize arguments for TEST/DEV env

    aca-py start \
        -it acapy_plugin_toolbox.http_ws 0.0.0.0 $HTTP_PORT \
        -ot http \
        -e "$HTTP_ENDPOINT" "${WS_ENDPOINT}" \
        --label "$AGENT_NAME" \
        --auto-accept-requests --auto-ping-connection \
        --auto-respond-credential-proposal --auto-respond-credential-offer --auto-respond-credential-request --auto-store-credential \
        --auto-respond-presentation-proposal --auto-respond-presentation-request --auto-verify-presentation \
        --invite --invite-role admin --invite-label "$AGENT_NAME (admin)" \
        --genesis-url https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_sandbox_genesis \
        --wallet-type indy \
        --plugin acapy_plugin_toolbox \
        --debug-connections \
        --debug-credentials \
        --debug-presentations \
        --enable-undelivered-queue
fi

