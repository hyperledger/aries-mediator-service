#!/bin/bash

if [ -z ${GENESIS_URL+x} ]; then
    GENESIS_URL=https://raw.githubusercontent.com/Indicio-tech/indicio-network/main/genesis_files/pool_transactions_testnet_genesis
fi

echo "Starting aca-py with:"
echo
echo "   DEPLOYMENT_ENV: $DEPLOYMENT_ENV"
echo "   HTTP_PORT: $HTTP_PORT"
echo "   WS_PORT: $WS_PORT"
echo "   HTTP_ENDPOINT: $HTTP_ENDPOINT"
echo "   WS_ENDPOINT: $WS_ENDPOINT"
echo "   AGENT_NAME: $AGENT_NAME"
echo "   WALLET_NAME: $WALLET_NAME"
echo "   WALLET_KEY: $WALLET_KEY"
echo "   RDBMS_URL: $RDBMS_URL"
echo "   GENESIS_URL: $GENESIS_URL"
echo
echo "Using the $DEPLOYMENT_ENV environment configuration."
echo

if [[ "$DEPLOYMENT_ENV" == "TEST" ]]; then

    aca-py start \
        -it http 0.0.0.0 $HTTP_PORT \
        -it acapy_plugin_toolbox.http_ws 0.0.0.0 $WS_PORT \
        -ot http \
        -e "$HTTP_ENDPOINT" "${WS_ENDPOINT}" \
        --label "$AGENT_NAME" \
        \
        --genesis-url $GENESIS_URL \
        \
        --connections-invite --invite-metadata-json '{"group": "admin"}' --invite-label "$AGENT_NAME (admin)" \
        --invite-multi-use \
        `# (JamesKEbert) Note: Once upgraded to ACA-Py 0.5.4, we may be able to use --wallet-local-did and --seed 30354388828352159037195346955238 to do either local or public automatic did generation for use in mediation.` \
        \
        --auto-accept-requests --auto-ping-connection \
        \
        --wallet-type indy \
        --wallet-storage-type postgres_storage \
        --wallet-storage-config "{\"url\": \"$RDBMS_URL\", \"wallet_scheme\": \"DatabasePerWallet\"}" \
        --wallet-storage-creds "$RDBMS_AUTH" \
        --wallet-name "$WALLET_NAME" \
	--wallet-key "$WALLET_KEY" \
	--auto-provision \
        \
        --log-config logging.ini \
        \
        --plugin acapy_plugin_toolbox \
	--open-mediation \
        --enable-undelivered-queue \
	--auto-send-keylist-update-in-create-invitation --auto-send-keylist-update-in-requests

else

    echo "Only the TEST environment is currently supported (given: DEPLOYMENT_ENV=$DEPLOYMENT_ENV)"

fi

