import asyncio
import logging

from kubernetes_asyncio import watch

from deployer.commands import redeploy

log = logging.getLogger(__name__)

type_mapping = {
    "ADDED": redeploy,
    "MODIFIED": redeploy,
}


async def monitor(crds, namespace):
    log.info(f"Monitoring charts.k8s.openttd.org in namespace {namespace} for changes ...")

    stream = watch.Watch().stream(crds.list_namespaced_custom_object, "k8s.openttd.org", "v1", namespace, "charts")
    async for event in stream:
        module = type_mapping.get(event["type"])
        if module:
            asyncio.ensure_future(module.handle_event(event))
