#!/usr/bin/env python3
# Copyright 2026 dparv
# See LICENSE file for licensing details.

"""Charm the application."""

import logging

import ops

# A standalone module for workload-specific logic (no charming concerns):
import forgejo_runner

logger = logging.getLogger(__name__)


class ForgejoRunnerCharmCharm(ops.CharmBase):
    """Charm the application."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on.install, self._on_install)
        framework.observe(self.on.start, self._on_start)
        framework.observe(self.on.update_status, self._on_update_status)
        framework.observe(self.on['register-runner'].action, self._on_register_runner)

    def _on_install(self, event: ops.InstallEvent):
        """Install the workload on the machine."""
        self.unit.status = ops.MaintenanceStatus("Installing forgejo-runner snap")
        forgejo_runner.install()
        self.unit.status = ops.ActiveStatus()

    def _on_start(self, event: ops.StartEvent):
        """Handle start event."""
        self.unit.status = ops.ActiveStatus("Please run 'register-runner' action to register the runner")
        version = forgejo_runner.get_version()
        if version is not None:
            self.unit.set_workload_version(version)

    def _on_register_runner(self, event: ops.ActionEvent):
        """Handle register-runner event."""
        self.unit.status = ops.MaintenanceStatus("Registering runner")
        try:
            host = event.params["host"]
            result = forgejo_runner.register_runner(event.params)
            if result:
                event.set_results({"result": f"Runner registered successfully at {host}"})
                self.unit.status = ops.ActiveStatus(f"runner registered at {host}")
            else:
                err_msg = f"Failed to register runner. Check host or credentials"
                logger.error(err_msg)
                event.fail(err_msg)
                self.unit.status = ops.BlockedStatus(f"failed to register runner at {host}")
        except Exception as e:
            exp_msg = f"Failed to register runner: {e}"
            logger.error(exp_msg)
            event.fail(exp_msg)
            self.unit.status = ops.BlockedStatus("failed to register runner")

    def _on_update_status(self, event: ops.UpdateStatusEvent):
        """Handle update-status event."""
        if not forgejo_runner.is_service_running():
            self.unit.status = ops.BlockedStatus("forgejo-runner service not running")
        else:
            host = forgejo_runner.get_host()
            self.unit.status = ops.ActiveStatus(f"runner registered at {host}")


if __name__ == "__main__":  # pragma: nocover
    ops.main(ForgejoRunnerCharmCharm)
