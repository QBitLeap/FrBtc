#!/usr/bin/env bash

# Stable internal RPC contract for dependent Umbrel apps.
export APP_FRACTAL_RPC_HOST="qbitleap-frbtc-fractal-node_fractald_1"
export APP_FRACTAL_RPC_PORT="8332"
export APP_FRACTAL_RPC_USER="fractalrpc"

# Match the APP_PASSWORD that umbreld derives for this app without writing the
# secret to the repository or exposing the RPC port on the host network.
export APP_FRACTAL_RPC_PASS="$(derive_entropy "app-${EXPORTS_APP_ID}-seed-APP_PASSWORD")"
export APP_FRACTAL_RPC_PASSWORD="${APP_FRACTAL_RPC_PASS}"
export APP_FRACTAL_NETWORK="mainnet"
export APP_FRACTAL_AUXPOW_CHAIN_ID="8228"
