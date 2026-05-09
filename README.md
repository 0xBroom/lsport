# lsport

A fast and elegant command-line utility for inspecting and managing TCP ports on macOS and Linux.

[![PyPI version](https://img.shields.io/pypi/v/lsport.svg)](https://pypi.org/project/lsport/)
[![Python versions](https://img.shields.io/pypi/pyversions/lsport.svg)](https://pypi.org/project/lsport/)
[![Downloads](https://img.shields.io/pypi/dm/lsport.svg)](https://pypi.org/project/lsport/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is lsport?

`lsport` helps you quickly identify which processes are occupying TCP ports and terminate them when needed. It provides three modes of operation:

- **List mode**: View all open TCP ports with process details
- **Kill mode**: Terminate a process occupying a specific port
- **Interactive mode**: Browse and manage ports through a TUI menu

## Features

- 🚀 Fast port scanning using `psutil`
- 🎨 Beautiful terminal output with `rich`
- 🔍 Filter by port state (LISTEN, ESTABLISHED, CLOSE_WAIT)
- 🛡️ Safe: asks for confirmation before killing processes
- 💪 Force kill option for stubborn processes
- 📊 Interactive TUI for easy port management

## Requirements

- macOS or Linux
- Python 3.9 or higher
- [`pipx`](https://pipx.pypa.io/) (one-time install)

## Installation

`lsport` is published on [PyPI](https://pypi.org/project/lsport/) and installed
in an isolated environment via [`pipx`](https://pipx.pypa.io/). This avoids
polluting your system Python, never touches `sudo`, and gives you a clean
`pipx uninstall lsport` when you're done.

### 1. Install pipx (one-time)

**macOS:**

```bash
brew install pipx
pipx ensurepath
```

**Linux (Debian/Ubuntu):**

```bash
sudo apt install pipx
pipx ensurepath
```

For other distributions or platforms see the [pipx installation guide](https://pipx.pypa.io/stable/installation/).

### 2. Install lsport

```bash
pipx install lsport
```

That's it. `lsport` is now available on your `PATH`, with its dependencies
isolated in a dedicated virtual environment under `~/.local/share/pipx/`.

### Updating

```bash
pipx upgrade lsport
```

### Uninstalling

```bash
pipx uninstall lsport
```

### Install from source

If you want to run a development build from a local clone (useful for
contributing — see [`CONTRIBUTING.md`](CONTRIBUTING.md)):

```bash
git clone https://github.com/0xBroom/lsport.git
cd lsport
pipx install --editable .
```

## Usage

### List all open ports

```bash
lsport list
```

Output example:
```
┌──────┬─────────────┬──────────┬──────┬────────────────┐
│ Port │ Protocol    │ State    │ PID  │ Process        │
├──────┼─────────────┼──────────┼──────┼────────────────┤
│ 3000 │ 0.0.0.0:3000│ LISTEN   │ 1234 │ node           │
│ 5432 │ 127.0.0.1:* │ LISTEN   │ 5678 │ postgres       │
└──────┴─────────────┴──────────┴──────┴────────────────┘
```

### Filter by state

```bash
# Show only listening ports
lsport list --state listen

# Show active connections
lsport list --state established

# Show ports in close_wait state
lsport list --state close_wait
```

### Kill a process on a specific port

```bash
# Interactive kill (asks for confirmation)
lsport kill 3000

# Skip confirmation
lsport kill 3000 --yes

# Force kill (SIGKILL instead of SIGTERM)
lsport kill 3000 --force
```

### Interactive mode

```bash
lsport interactive
```

Navigate the interactive TUI to:
- Browse all LISTEN ports
- Select ports by row number or port number
- Kill processes with confirmation

## Command Reference

### `lsport list`

Lists all open TCP ports.

**Options:**
- `-s, --state [listen|established|close_wait]` - Filter by connection state

### `lsport kill <port>`

Terminates the process occupying the specified port.

**Options:**
- `-f, --force` - Use SIGKILL instead of SIGTERM
- `-y, --yes` - Skip confirmation prompt

### `lsport interactive`

Launch an interactive TUI to browse and manage ports.

## Development

### Project structure

```
lsport/
├── lsport.py      # Main CLI application
├── pyproject.toml  # Package metadata and entry point
├── LICENSE         # MIT License
└── README.md       # This file
```

### Dependencies

- [`psutil`](https://github.com/giampaolo/psutil) - Process and system utilities
- [`typer`](https://github.com/tiangolo/typer) - CLI framework
- [`rich`](https://github.com/Textualize/rich) - Terminal formatting and TUI

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Created by Esteban Encina

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)
- Inspired by the need for a fast, native port management tool for the terminal
