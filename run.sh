#!/bin/sh
#
# Startup script for the container.
#

set -e

# Start a local tiller and make sure the rest connect to it
tiller --history-max 10 --storage secret &
export HELM_HOST=":44134"
sleep 1

# Make sure openttd-base is updated (it is not monitored by deployer, and can
# only ever change if this container is redeployed anyway).
helm dep update /charts/openttd-base
helm upgrade --force --namespace global --install global-openttd-base -f /config/global/global.yaml -f /config/global/openttd-base.yaml /charts/openttd-base

cd /code
python -m deployer
