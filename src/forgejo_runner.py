# Copyright 2026 dparv
# See LICENSE file for licensing details.

"""Functions for managing and interacting with the workload.

The intention is that this module could be used outside the context of a charm.
"""

import logging
import os

logger = logging.getLogger(__name__)


def install() -> None:
    """Install the forgejo-runner snap and connect to docker intrefaces."""
    os.system("snap install forgejo-runner --channel edge")
    os.system("snap connect forgejo-runner:docker docker:docker-daemon")
    os.system("snap connect forgejo-runner:docker-executables docker:docker-executables")


def start() -> None:
    """Start the workload (by running a commamd, for example)."""
    pass

def get_version() -> str | None:
    """Get the running version of the workload."""
    # You'll need to implement this function (or remove it if not needed).
    return None

def register_runner(params):
    """Register the runner to a forgejo instance."""
    host = params["host"]
    secret = params["secret"]
    cmd = f"snap set forgejo-runner host=\"{host}\" secret=\"{secret}\""
    os.system(cmd)
