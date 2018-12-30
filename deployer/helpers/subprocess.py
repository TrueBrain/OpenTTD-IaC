import asyncio
import shlex


class CommandError(Exception):
    """Thrown if the exit code of the command was non-zero."""


async def run_command(command, cwd=None, capture_stdout=False):
    process = await asyncio.create_subprocess_exec(
        *shlex.split(command),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )

    return_code = await process.wait()
    if return_code != 0:
        stderr = []
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            stderr.append(line.decode())

        raise CommandError(return_code, command, "\n".join(stderr))

    if capture_stdout:
        stdout = []
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            stdout.append(line.decode())

        return stdout
