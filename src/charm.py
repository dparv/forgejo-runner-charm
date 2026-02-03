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
        framework.observe(self.on['register-runner'].action, self._on_register_runner)

    def _on_install(self, event: ops.InstallEvent):
        """Install the workload on the machine."""
        self.unit.status = ops.MaintenanceStatus("Installing forgejo-runner snap")
        forgejo_runner.install()
        self.unit.status = ops.ActiveStatus()

    def _on_start(self, event: ops.StartEvent):
        """Handle start event."""
        self.unit.status = ops.MaintenanceStatus("Starting workload")
        forgejo_runner.start()
        version = forgejo_runner.get_version()
        if version is not None:
            self.unit.set_workload_version(version)
        self.unit.status = ops.ActiveStatus()

    def _on_register_runner(self, event: ops.ActionEvent):
        """Handle register-runner event."""
        self.unit.status = ops.MaintenanceStatus("Registering runner")
        try:
            forgejo_runner.register_runner(event.params)
            self.unit.status = ops.ActiveStatus("runner registered")
        except Exception as e:
            logger.error(f"Failed to register runner: {e}")
            self.unit.status = ops.BlockedStatus("failed to register runner")


if __name__ == "__main__":  # pragma: nocover
    ops.main(ForgejoRunnerCharmCharm)
