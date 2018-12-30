import asyncio
import logging

from kubernetes_asyncio import client, config

from deployer.monitor import monitor


async def main():
    try:
        config.load_incluster_config()
    except:
        await config.load_kube_config()
    crds = client.CustomObjectsApi()

    await monitor(crds)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
