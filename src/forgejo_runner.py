# Copyright 2026 dparv
# See LICENSE file for licensing details.

"""Functions for managing and interacting with the workload.

The intention is that this module could be used outside the context of a charm.
"""

import logging
import subprocess

from charms.operator_libs_linux.v2 import snap
from charms.operator_libs_linux.v1.systemd import service_running


logger = logging.getLogger(__name__)

SYSTEMD_SERVICE = "snap.forgejo-runner.forgejo-runner.service"


def _get_runner_snap() -> snap.Snap:
    cache = snap.SnapCache()
    return cache["forgejo-runner"]

def install() -> None:
    """Install the forgejo-runner snap and connect to docker intrefaces."""
    runner = _get_runner_snap()
    runner.ensure(snap.SnapState.Latest, channel="edge")
    runner.connect(plug="docker", service="docker", slot="docker-daemon")
    runner.connect(plug="docker-executables", service="docker", slot="docker-executables")

def get_version() -> str | None:
    """Get the running version of the workload."""
    try:
        runner = _get_runner_snap()
        if runner.present and runner.version:
            # Keep the previous behaviour: return without a leading "v".
            return runner.version.lstrip("v")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get forgejo-runner version: {e}")
    except snap.Error as e:
        logger.error(f"Failed to query forgejo-runner snap: {e}")

    # Fallback: call the workload binary directly (the snap library may not have version
    # populated, depending on snapd response).
    try:
        result = subprocess.run(
            ["/snap/forgejo-runner/current/bin/forgejo-runner", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        version = result.stdout.strip()
        version = version.replace("forgejo-runner version v", "")
        return version
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get forgejo-runner version from binary: {e}")
    return None

def register_runner(params) -> bool:
    """Register the runner to a forgejo instance."""
    host = params["host"]
    secret = params["secret"]
    runner = _get_runner_snap()
    runner.set({"host": host, "secret": secret})
    return is_service_running()

def is_service_running() -> bool:
    """Check if the forgejo-runner service has failed."""
    return service_running(SYSTEMD_SERVICE)

def get_host() -> str:
    """Get the configured host for the runner."""
    runner = _get_runner_snap()
    return runner.get("host")
