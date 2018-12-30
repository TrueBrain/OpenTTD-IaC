#!/bin/sh
#
# Startup script for the container.
#

# When we get the TERM signal, forward it to deployer
_term() {
    if [ -n "${deployer_pid}" ]; then
        kill ${deployer_pid}
    fi
    if [ -n "${tiller_pid}" ]; then
        kill ${tiller_pid}
    fi
}
trap _term INT TERM

# Start a local tiller and make sure the rest connect to it
TILLER_NAMESPACE=global linux-amd64/tiller --history-max 10 --storage secret &
tiller_pid=$!

# Start the deployer
HELM_HOST=":44134" python -m deployer &
deployer_pid=$!
wait "${deployer_pid}"

# If the deployer stops, stop tiller too
kill ${tiller_pid}
