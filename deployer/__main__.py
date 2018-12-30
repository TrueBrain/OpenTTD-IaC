import asyncio
import functools
import logging
import signal

from kubernetes_asyncio import client, config

from deployer.monitor import monitor

log = logging.getLogger(__name__)


def signal_handler(tasks, signum, frame):
    log.info("SIGTERM received; shutting down ..")
    for task in tasks:
        task.cancel()


async def main():
    try:
        config.load_incluster_config()
    except:
        await config.load_kube_config()
    crds = client.CustomObjectsApi()

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
