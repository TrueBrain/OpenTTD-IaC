import glob
import json
import logging
import os
import tempfile

from deployer.helpers.subprocess import run_command

log = logging.getLogger(__name__)


async def _check_needs_deployment(namespace, chart, app_version):
    raw_json = await run_command(f"helm ls "
                                 f"--namespace {namespace} "
                                 f"\"^{namespace}-{chart}$\" "
                                 f"--output json",
                                 capture_stdout=True)
    data = json.loads(raw_json[0])

    if len(data["Releases"]) != 1:
        raise Exception(f"'helm ls' reported multiple version for '{namespace}-{chart}'; this should not be possible")

    current_app_version = data["Releases"][0]["AppVersion"]

    return current_app_version != app_version


async def _deploy(namespace, chart, app_version):
    with tempfile.TemporaryDirectory() as dest:
        if os.path.exists(f"charts/{chart}/requirements.yaml"):
            extra = "-u"
        else:
            extra = ""

        await run_command(f"helm package "
                          f"{extra} "
                          f"--app-version {app_version} "
                          f"charts/{chart} "
                          f"-d {dest}")

        # Validate that a single package was created and find what the filename is
        files = glob.glob(f"{dest}/{chart}*.tgz")
        if len(files) != 1:
            raise Exception("Expected one package tgz, found %d" % len(files))

        await run_command(f"helm upgrade "
                          f"--force "
                          f"--namespace {namespace} "
                          f"--install {namespace}-{chart} "
                          f"-f config/{namespace}/global.yaml "
                          f"-f config/{namespace}/{chart}.yaml "
                          f"{files[0]}")


async def handle_event(event):
    namespace = event["object"]["metadata"]["namespace"]
    chart = event["object"]["metadata"]["name"]
    app_version = event["object"]["spec"]["appversion"]

    needs_deployment = await _check_needs_deployment(namespace, chart, app_version)

    if not needs_deployment:
        log.info(f"[{namespace}-{chart}] Already at {app_version}")
        return

    log.info(f"[{namespace}-{chart}] Deploying {app_version} ..")

    try:
        await _deploy(namespace, chart, app_version)
    except Exception as e:
        log.exception(e)
        log.error(f"[{namespace}-{chart}] Deploying {app_version} FAILED")
    else:
        log.info(f"[{namespace}-{chart}] Deploying {app_version} DONE")
