# Forgejo Runner Charm

A Juju machine charm that installs and manages the **Forgejo Runner** snap, intended for running Forgejo Actions/CI jobs on Juju units.

Today this charm focuses on:

- Installing the `forgejo-runner` snap (currently from the `edge` channel)
- Connecting the snap to Docker interfaces
- Providing a `register-runner` action to register/configure the runner against a Forgejo server

## Requirements

- Juju (for deploying the charm)
- A model running on machines (e.g., LXD, MAAS, etc.)
- Units based on **Ubuntu 24.04** (this is the charm base)
- Docker available on the unit
  - The charm connects snap interfaces to `docker:docker-daemon` and `docker:docker-executables`.
  - You can provide Docker however you prefer (e.g., install the Docker snap on the machine).

## Deploy

If you already have a built charm artifact in this repo (for example `forgejo-runner_amd64.charm`):

```bash
juju deploy ./forgejo-runner_amd64.charm forgejo-runner
juju status --watch 1s
```

If you want to build the charm yourself, you can use `charmcraft`:

```bash
charmcraft pack
juju deploy ./forgejo-runner_*.charm forgejo-runner
```

## Register the runner (action)

After deployment, register the runner against your Forgejo instance using the `register-runner` action.

The action expects:

- `host`: Forgejo server URL (e.g., `https://forgejo.example.com`)
- `secret`: the *registration secret* (not the runner token)

Example:

```bash
juju run forgejo-runner/0 register-runner host=https://forgejo.example.com secret=REDACTED
```

Notes:

- Treat the secret as sensitive; avoid putting it into shell history.
- Internally, the action sets snap configuration via `snap set forgejo-runner host=... secret=...`.
- NB! The registration secret for the runner. Mind that this is NOT
as the token. This secret is obtained by running the forgejo-cli command
on the Forgejo server, as an example below:
`forgejo forgejo-cli actions register --secret $SECRET`
`forgejo forgejo-cli actions register --secret $SECRET --labels "docker"`

## What the charm does

On `install`:

- Installs the `forgejo-runner` snap from the `edge` channel
- Connects interfaces:
  - `forgejo-runner:docker` → `docker:docker-daemon`
  - `forgejo-runner:docker-executables` → `docker:docker-executables`

On `start`:

- Marks the unit active
- Attempts to set a workload version if available

## Limitations / TODO

This repository is still early-stage:

- `src/forgejo_runner.py:start()` is currently a stub.
- `src/forgejo_runner.py:get_version()` currently returns `None`, so workload version is not set.

If you implement `get_version()`, you can also enable the (currently skipped) integration test that asserts the workload version.

## Development

This project uses:

- `tox` for linting/formatting/tests
- `ruff` for formatting and linting
- `pyright` for type-checking
- `pytest` for unit/integration tests
- `uv` (via the charmcraft `uv` plugin) for dependency management

### Common tasks

Format:

```bash
tox -e format
```

Lint + type-check:

```bash
tox -e lint
```

Unit tests:

```bash
tox -e unit
```

Integration tests (requires a working Juju controller):

```bash
tox -e integration
```

The integration suite will deploy a charm from:

- `CHARM_PATH` if set, otherwise
- the single `*.charm` file found in the repo root

Example:

```bash
CHARM_PATH=./forgejo-runner_amd64.charm tox -e integration
```

## Troubleshooting

- Check status: `juju status`
- View logs: `juju debug-log --replay --tail`
- Inspect action results: `juju run <unit> register-runner ... --wait`
- On the unit:
  - `snap list | grep forgejo-runner`
  - `snap connections forgejo-runner`
  - `snap get forgejo-runner`

## Project layout

- `src/charm.py`: Juju charm code
- `src/forgejo_runner.py`: workload helpers (snap install/config)
- `tests/unit`: ops testing harness tests
- `tests/integration`: Jubilant-based integration tests
