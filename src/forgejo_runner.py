# Copyright 2026 dparv
# See LICENSE file for licensing details.

"""Functions for managing and interacting with the workload.

The intention is that this module could be used outside the context of a charm.
"""

import logging
import subprocess
import os
from charms.operator_libs_linux.v1.systemd import service_running


logger = logging.getLogger(__name__)

SYSTEMD_SERVICE = "snap.forgejo-runner.forgejo-runner.service"

def install() -> None:
    """Install the forgejo-runner snap and connect to docker intrefaces."""
    # Install the forgejo-runner snap from the edge channel
    subprocess.run(["snap", "install", "forgejo-runner", "--channel", "edge"], check=True)
    # Connect the required interfaces
    subprocess.run(["snap", "connect", "forgejo-runner:docker", "docker:docker-daemon"], check=True)
    # Connect the docker-executables interface
    subprocess.run(["snap", "connect", "forgejo-runner:docker-executables", "docker:docker-executables"], check=True)

def get_version() -> str | None:
    """Get the running version of the workload."""
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
        logger.error(f"Failed to get forgejo-runner version: {e}")
    return None

def register_runner(params) -> bool:
    """Register the runner to a forgejo instance."""
    host = params["host"]
    secret = params["secret"]
    cmd = f"snap set forgejo-runner host=\"{host}\" secret=\"{secret}\""
    subprocess.run(cmd, shell=True, check=True)
    return is_service_running()

def is_service_running() -> bool:
    """Check if the forgejo-runner service has failed."""
    return service_running(SYSTEMD_SERVICE)

def get_host() -> str:
    """Get the configured host for the runner."""
    result = subprocess.run(
        ["snap", "get", "forgejo-runner", "host"],
        check=True,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()
