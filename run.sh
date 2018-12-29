#!/bin/sh
#
# Startup script for the container.
#

set -e

tiller --history-max 10 --storage secret &
sleep 1

./initial-startup.sh
python -m deployer
