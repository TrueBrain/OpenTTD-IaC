#!/bin/sh
#
# Script to initial deploy OpenTTD's infrastructure on kubernetes.
#
# Every chart that is under 'global/' is being deployed. Mainly this is
# openttd-base, which contains things like cert-manager, nginx-ingress, etc.
#
# It also prepares kubernetes to run with 'deployer', and starts an initial
# version of that pod. After this, 'deployer' takes over and deploys the rest
# of the OpenTTD's infrastructure, and will keep monitoring for change
# requests.
#

set -e

kubectl apply -f config/namespaces.yaml
kubectl apply -f config/deployer-service-account.yaml

for chart in $(cd config/global && ls *.yaml); do
    chart=$(echo ${chart} | sed 's/.yaml$//')
    if [ "${chart}" = "global" ]; then continue; fi

    if [ -e charts/${chart}/requirements.yaml ]; then
        helm dep update charts/${chart}
    fi

    helm upgrade --force --namespace global --install global-${chart} -f config/global/global.yaml -f config/global/${chart}.yaml charts/${chart}
done
