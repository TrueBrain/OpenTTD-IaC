#!/bin/sh
#
# Startup script for the container.
#

set -e

# Start a local tiller and make sure the rest connect to it
tiller --history-max 10 --storage secret &
sleep 1

HELM_HOST=":44134" python -m deployer
