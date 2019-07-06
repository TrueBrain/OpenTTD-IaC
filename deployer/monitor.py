import asyncio
import logging

from kubernetes_asyncio import watch

from deployer.commands import redeploy

log = logging.getLogger(__name__)

type_mapping = {
    "ADDED": redeploy,
    "MODIFIED": redeploy,
}


def _emit_event(event):
    module = type_mapping.get(event["type"])
    if module:
        asyncio.ensure_future(module.handle_event(event))


async def monitor(crds, namespace):
    log.info(f"Monitoring charts.k8s.openttd.org in namespace '{namespace}' for changes ...")

    # Prepare what function we want to call with which parameters
    func = crds.list_namespaced_custom_object
    args = ["k8s.openttd.org", "v1", namespace, "charts"]

    # Start by listing all entries, and emit an 'ADDED' for each existing
    # entry. This allows us to get in a known-good-state, and monitor all
    # changes after.
    initial_list = await func(*args)
    for item in initial_list['items']:
        _emit_event({"type": "ADDED", "object": item})

    # The list has the resource_version we should use as starting point of
    # our watch().
    resource_version = initial_list['metadata']['resourceVersion']

    my_watch = watch.Watch()
    # XXX - kubernetes-asyncio has not sync'd with upstream yet.
    # See https://github.com/kubernetes-client/python-base/commit/2d69e89dab7134186cbcdaf82381ab6295c6c394
    # and https://github.com/tomplus/kubernetes_asyncio/issues/77
    # If this gets fixed, the next line can be removed.
    my_watch.resource_version = resource_version

    async with my_watch.stream(func, *args, resource_version=resource_version, _request_timeout=30) as stream:
        async for event in stream:
            _emit_event(event)

    log.error(f"Monitoring in namespace '{namespace}' stopped unexpectedly")
