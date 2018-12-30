#!/bin/sh
#
# Startup script for the container.
#

set -e

# Start a local tiller and make sure the rest connect to it
tiller --history-max 10 --storage secret &
export HELM_HOST=":44134"
sleep 1

cd /code
python -m deployer
