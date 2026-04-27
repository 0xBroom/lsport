# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/0xBroom/portctl/releases/tag/v0.1.0
