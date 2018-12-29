# OpenTTD-IaC

This "Infrastructure as Code" repository specifies how our infrastructure
looks like. Most of this infrastructure runs on kubernetes, and this
repository in fact is a pod that runs in the kubernetes, managing the rest
of the pods (which pods, which versions, etc).

## Getting started

To setup a development system with this repository, get yourself access
to a kubernetes cluster. This can be MiniKube, or any other. After that,
simply run:

```bash
./bootstrap.sh
```

This will prepare the cluster with a service account, namespaces, and
an initial container (openttd-iac), which will take over from there.

## How does it work?

Part of the openttd-iac container is 'deployer', which monitors a Customer
Resource Definition called Chart.k8s.openttd.org. This chart indicates
what version of what pods to run on the cluster. Because of this, the cluster
is self-maintaining. After the initial bootstrap, you only need to set this
CRD to the correct value to deploy a new version of a pod.

## How do I add a new service?

A new service means both a new container (which you should do in another
repository), and a new chart (which you should do in this repository). After
this repository is tagged (and as such deployed on production), the chart
becomes available. Via the above mentioned CRD you can now define this
chart to become active.
