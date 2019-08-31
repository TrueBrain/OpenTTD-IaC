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

helm repo add jetstack https://charts.jetstack.io

kubectl apply -f config/namespaces.yaml
kubectl apply -f config/crd-charts.yaml
kubectl apply -f config/sa-azure-pipelines.yaml
kubectl apply -f config/sa-deployer.yaml
kubectl apply -f config/sa-fluentd.yaml

# External CRDs; helm doesn't support CRDs that well, so we apply it manually
kubectl apply -f https://raw.githubusercontent.com/jetstack/cert-manager/master/deploy/manifests/00-crds.yaml

for i in $(ls secrets/*.yaml); do
    kubectl apply -f ${i}
done

# Install openttd-base. This is the only package not monitored/deployed by
# deployer.This is mainly because it needs a ton of access to do so, which is
# unwise to assign to a single pod.
helm dep update charts/openttd-base
helm upgrade \
    --force \
    --namespace global \
    --set cert-manager.createCustomResource=false \
    --install global-openttd-base \
    -f config/global/global.yaml \
    -f config/global/openttd-base.yaml \
    charts/openttd-base

# Deploy openttd-iac for the first time. This contains the deployer, and will
# take over from there.
helm upgrade \
    --force \
    --namespace global \
    --install global-openttd-iac \
    -f config/global/global.yaml \
    -f config/global/openttd-iac.yaml \
    charts/openttd-iac
