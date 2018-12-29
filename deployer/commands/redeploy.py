import glob
import logging
import os
import tempfile

from deployer.helpers.subprocess import run_command

log = logging.getLogger(__name__)


async def _deploy(namespace, chart, app_version):
    with tempfile.TemporaryDirectory() as dest:
        if os.path.exists(f"charts/{chart}/requirements.yaml"):
            extra = "-u"
        else:
            extra = ""

        await run_command(f"helm package {extra} --app-version {app_version} /charts/{chart} -d {dest}")

        # Validate that a single package was created and find what the filename is
        files = glob.glob(f"{dest}/{chart}*.tgz")
        if len(files) != 1:
            raise Exception("Expected one package tgz, found %d" % len(files))

        await run_command(f"helm upgrade --force --namespace {namespace} --install {namespace}-{chart} -f /config/{namespace}/global.yaml -f /config/{namespace}/{chart}.yaml {files[0]}")


async def handle_event(event):
    namespace = event["object"]["metadata"]["namespace"]
    chart = event["object"]["metadata"]["name"]
    app_version = event["object"]["spec"]["appversion"]

    log.info(f"[{namespace}-{chart}] Deploying {app_version} ..")

    try:
        await _deploy(namespace, chart, app_version)
    except Exception:
        log.error(f"[{namespace}-{chart}] Deploying {app_version} FAILED")

    log.info(f"[{namespace}-{chart}] Deploying {app_version} DONE")
