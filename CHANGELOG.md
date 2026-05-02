# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-05-02

### Added

- Linux support. `portctl` is now distributed as an OS-independent Python package
  and verified working on Debian/Ubuntu in addition to macOS.
- `pyproject.toml` classifier `Operating System :: POSIX :: Linux`.

### Changed

- **Installation now uses [`pipx`](https://pipx.pypa.io/)** instead of the legacy
  `install.sh` script. New install flow is `pipx install .` from a clone of the
  repository. See `README.md` for the full instructions, including how to install
  `pipx` itself on each supported OS.
- `CONTRIBUTING.md` development setup now uses `pipx install --editable .` for
  live-edit local development, replacing the prior manual symlink approach.
- Bumped version to `0.2.0` to reflect the breaking change in the installation
  contract.

### Removed

- `install.sh`. The script mutated the repository's source shebang via `sed`,
  symlinked into `/usr/local/bin` (a root-trusted PATH) pointing to a
  user-writable target, used `pip install --break-system-packages` to bypass
  PEP 668, and appended non-idempotent entries to `~/.zshrc` with no
  uninstall counterpart. All four issues are eliminated by adopting `pipx`,
  which installs into an isolated per-tool virtual environment under
  `~/.local/share/pipx/` and exposes a symmetric `pipx uninstall portctl`.

### Fixed

- Closes #1 (`install.sh` mutated source via `sed`).
- Closes #2 (privilege-escalation surface via `/usr/local/bin/portctl` →
  user-writable target).
- Closes #3 (unpinned `pip install` with `--break-system-packages` fallback).
- Closes #4 (non-idempotent `~/.zshrc` mutation, missing `uninstall.sh`).

## [0.1.0] - 2026-04-27

### Added

- Initial release of `portctl` CLI for macOS.
- `list` command to inspect open TCP ports.
- `kill` command to terminate processes by port with confirmation, `--yes`, and `--force` options.
- `interactive` command for TUI-based port inspection and termination.
- Rich terminal UI with tables, panels, and color-coded connection states.
- Installer script (`install.sh`) for macOS environments.
- Python packaging support via `pyproject.toml`.
- Development dependency management via `requirements.txt`.
- MIT license.
- Project documentation (`README.md`, `CONTRIBUTING.md`).
- Community standards documentation (`CODE_OF_CONDUCT.md`).
- Test suite (unit and CLI integration tests with pytest).

### Changed

- Translated CLI output and installer messages from Spanish to English.
- Improved type annotations and formatting consistency.
- Added linting and formatting configuration via Ruff.

[0.2.0]: https://github.com/0xBroom/portctl/releases/tag/v0.2.0
[0.1.0]: https://github.com/0xBroom/portctl/releases/tag/v0.1.0
