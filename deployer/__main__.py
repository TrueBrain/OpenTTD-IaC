import asyncio
import functools
import logging
import os
import sentry_sdk
import signal

from kubernetes_asyncio import client, config

from deployer.helpers.subprocess import run_command
from deployer.monitor import monitor

log = logging.getLogger(__name__)


def signal_handler(tasks, signum, frame):
    log.info("SIGTERM received; shutting down ..")
    for task in tasks:
        task.cancel()


async def main():
    # Setup Sentry if configured
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        with open(".version") as f:
            release = f.readline().strip()
        environment = os.getenv("HOSTNAME", "dev").split("-")[0]

        sentry_sdk.init(
            sentry_dsn,
            release=release,
            environment=environment)
        log.info("Sentry initialized with release='%s' and environment='%s'", release, environment)

    try:
        config.load_incluster_config()
    except Exception:
        await config.load_kube_config()
    crds = client.CustomObjectsApi()

    # Give tiller time to start up, if it isn't already
    log.info("Waiting for tiller to be available ..")
    await run_command(f"helm version", timeout=30)

    tasks = [
        asyncio.ensure_future(monitor(crds, "global")),
        asyncio.ensure_future(monitor(crds, "production")),
        asyncio.ensure_future(monitor(crds, "staging")),
    ]

    signal.signal(signal.SIGTERM, functools.partial(signal_handler, tasks))

    await asyncio.wait(tasks)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="[deployer] %Y/%m/%d %H:%M:%S",
        level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
