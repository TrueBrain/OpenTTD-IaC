#!/bin/sh
#
# Startup script for the container.
#

# Start a local tiller and make sure the rest connect to it
TILLER_NAMESPACE=global tiller --history-max 10 --storage secret &
tiller_pid=$!
sleep 1

HELM_HOST=":44134" python -m deployer
exit_code=$?

# If the deployer stops, stop tiller too
kill ${tiller_pid}

exit ${exit_code}
