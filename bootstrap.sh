#!/bin/sh
#
# Bootstrap the OpenTTD's infrastructure on kubernetes.
#
# This script only needs to be run once per kubernetes cluster. It prepares
# the cluster to run the 'OpenTTD-IaC' container, which takes over from
# there.
#
# It prepares kubernetes to run with 'deployer', and starts an initial version
# of that pod, together with service accounts, namespaces, etc.
#

set -e

kubectl apply -f config/namespaces.yaml
kubectl apply -f config/deployer-service-account.yaml

helm upgrade --force --namespace global --install global-openttd-iac -f config/global/global.yaml -f config/global/openttd-iac.yaml charts/openttd-iac
