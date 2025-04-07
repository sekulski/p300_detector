# EEG Project with BrainAccess SDK

This project provides tools and a GUI interface to work with EEG data using the BrainAccess SDK. 
It uses PyQt6 for the interface, and integrates various utilities for signal processing and development workflows.

---

## Setup Dev Environment

To set up the development environment, run:

```bash
poetry install
poetry run pre-commit install
```

---

## Requirements

- `bluetoothctl` must be installed and available in your system.
- The BrainAccess SDK must be available at such relative path:
  ```
  ../BrainAccessSDK-linux/python_api
  ```
  This path is referenced in `pyproject.toml` and used as a local dependency. Make sure the SDK is properly cloned or extracted there.

---

## Running Scripts

Before running any scripts using Poetry (e.g. GUI, test modules), you must first set the `PYTHONPATH` so local imports work correctly:

```bash
export PYTHONPATH=./
poetry run some/path/to/file.py
```

Alternatively, you can use a wrapper script or `make` task to automate this if needed.

---

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com) to enforce formatting and basic linting. Hooks include:

- `black` – code formatting
- `isort` – import sorting
- `flake8` – code linting

They will run automatically before each commit. You can also trigger them manually:

```bash
poetry run pre-commit run --all-files
```

---

## Testing

Run tests using:

```bash
poetry run pytest
```