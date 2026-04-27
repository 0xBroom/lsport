# portctl

A fast and elegant macOS command-line utility for inspecting and managing TCP ports.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## What is portctl?

`portctl` helps you quickly identify which processes are occupying TCP ports on your Mac and terminate them when needed. It provides three modes of operation:

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

- macOS (tested on recent versions)
- Python 3.9 or higher

## Installation

### Quick install (recommended)

Clone the repository and run the installer:

```bash
git clone https://github.com/0xBroom/portctl.git
cd portctl
bash install.sh
```

The installer will:
1. Verify Python 3 is installed (installs via Homebrew if missing)
2. Install required dependencies (`psutil`, `typer`, `rich`)
3. Symlink `portctl` to `/usr/local/bin`

### Manual installation

```bash
# Install dependencies
pip install psutil typer rich

# Make script executable
chmod +x portctl.py

# Symlink to your PATH
sudo ln -sf "$(pwd)/portctl.py" /usr/local/bin/portctl
```

## Usage

### List all open ports

```bash
portctl list
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
portctl list --state listen

# Show active connections
portctl list --state established

# Show ports in close_wait state
portctl list --state close_wait
```

### Kill a process on a specific port

```bash
# Interactive kill (asks for confirmation)
portctl kill 3000

# Skip confirmation
portctl kill 3000 --yes

# Force kill (SIGKILL instead of SIGTERM)
portctl kill 3000 --force
```

### Interactive mode

```bash
portctl interactive
```

Navigate the interactive TUI to:
- Browse all LISTEN ports
- Select ports by row number or port number
- Kill processes with confirmation

## Command Reference

### `portctl list`

Lists all open TCP ports.

**Options:**
- `-s, --state [listen|established|close_wait]` - Filter by connection state

### `portctl kill <port>`

Terminates the process occupying the specified port.

**Options:**
- `-f, --force` - Use SIGKILL instead of SIGTERM
- `-y, --yes` - Skip confirmation prompt

### `portctl interactive`

Launch an interactive TUI to browse and manage ports.

## Development

### Project structure

```
portctl/
├── portctl.py      # Main CLI application
├── install.sh      # macOS installer script
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
- Inspired by the need for a fast, native macOS port management tool
