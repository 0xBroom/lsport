#!/usr/bin/env python3
"""
portctl - Fast and elegant TCP port management for macOS and Linux
"""

__version__ = "0.2.0"

import os
import signal
from typing import Optional

import psutil
import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

VALID_STATES = ("LISTEN", "ESTABLISHED", "CLOSE_WAIT")

app = typer.Typer(
    help=(
        "🔌 portctl — Inspect and manage open TCP ports.\n\n"
        "Available commands:\n\n"
        "  list          List all open ports (TCP).\n"
        "                Use -s/--state to filter by state.\n\n"
        "  kill <port>   Terminate the process occupying that port.\n"
        "                Asks for confirmation before acting.\n\n"
        "  interactive   Interactive menu: select and close ports\n"
        "                with navigation by row number or port number.\n\n"
        "Available states for -s/--state:\n\n"
        "  listen        Ports waiting for incoming connections.\n"
        "  established   Active connections right now.\n"
        "  close_wait    Connections being closed by the remote side."
    ),
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def get_open_ports(filter_port: Optional[int] = None, filter_state: Optional[str] = None) -> list[dict]:
    ports = []
    seen = set()
    state_filter = filter_state.upper() if filter_state else None

    for proc in psutil.process_iter(["pid", "name", "username"]):
        try:
            conns = proc.net_connections(kind="tcp")
            for conn in conns:
                if not conn.laddr or conn.status not in VALID_STATES:
                    continue
                if state_filter and conn.status != state_filter:
                    continue
                port = conn.laddr.port
                key = (port, proc.pid, conn.status)
                if key in seen:
                    continue
                if filter_port and port != filter_port:
                    continue
                seen.add(key)
                ports.append(
                    {
                        "port": port,
                        "pid": proc.pid,
                        "name": proc.info["name"] or "?",
                        "user": proc.info["username"] or "?",
                        "status": conn.status,
                        "proto": "TCP",
                        "addr": str(conn.laddr.ip),
                    }
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    ports.sort(key=lambda x: x["port"])
    return ports


def status_color(status: str) -> str:
    return {"LISTEN": "green", "ESTABLISHED": "cyan", "CLOSE_WAIT": "yellow"}.get(status, "white")


def build_table(ports: list[dict], selected: Optional[set] = None) -> Table:
    table = Table(
        box=box.ROUNDED,
        border_style="bright_black",
        header_style="bold white on #1a1a2e",
        show_lines=False,
        pad_edge=True,
    )
    table.add_column("#", style="bright_black", width=4, justify="right")
    table.add_column("Port", style="bold yellow", width=8, justify="right")
    table.add_column("Proto", style="blue", width=6)
    table.add_column("Address", style="bright_black", width=16)
    table.add_column("State", width=13)
    table.add_column("PID", style="magenta", width=7, justify="right")
    table.add_column("Process", style="white", width=20)
    table.add_column("User", style="bright_black", width=12)

    for i, p in enumerate(ports, 1):
        color = status_color(p["status"])
        sel_mark = "✓ " if selected and p["port"] in selected else "  "
        row_style = "on #1c1c1c" if selected and p["port"] in selected else ""
        table.add_row(
            f"{sel_mark}{i}",
            str(p["port"]),
            p["proto"],
            p["addr"],
            Text(p["status"], style=f"bold {color}"),
            str(p["pid"]),
            p["name"][:20],
            p["user"][:12],
            style=row_style,
        )
    return table


def kill_port(port: int, force: bool = False) -> bool:
    killed = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for conn in proc.net_connections(kind="tcp"):
                if conn.laddr and conn.laddr.port == port:
                    os.kill(proc.pid, signal.SIGKILL if force else signal.SIGTERM)
                    killed.append(proc.pid)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, ProcessLookupError):
            continue
    return len(killed) > 0


# ─── Commands ───────────────────────────────────────────────────────────────


@app.command(
    "list",
    help=(
        "List open ports on the system.\n\n"
        "Without options, shows all (LISTEN, ESTABLISHED, CLOSE_WAIT).\n"
        "Use -s/--state to filter by a specific state.\n\n"
        "Examples:\n\n"
        "  portctl list\n"
        "  portctl list -s listen\n"
        "  portctl list -s established\n"
        "  portctl list -s close_wait"
    ),
)
def cmd_list(
    state: Optional[str] = typer.Option(
        None,
        "--state",
        "-s",
        help="Filter by state: listen | established | close_wait",
        metavar="STATE",
    ),
):
    if state and state.upper() not in VALID_STATES:
        console.print(
            f"[red]✗[/]  Unknown state: [bold]{state}[/]\n"
            f"    Valid values: [cyan]listen[/] · [cyan]established[/] · [cyan]close_wait[/]"
        )
        raise typer.Exit(1)

    ports = get_open_ports(filter_state=state)

    if not ports:
        hint = f" with state [bold]{state.upper()}[/]" if state else ""
        console.print(Panel(f"[yellow]No open ports found[/]{hint}", border_style="yellow"))
        return

    label = f"[bold white]🔌 portctl[/] [bright_black]—[/] [cyan]{len(ports)} ports found[/]"
    if state:
        label += f"  [bright_black]({state.upper()})[/]"

    console.print()
    console.print(Panel(label, border_style="bright_black", expand=False))
    console.print(build_table(ports))
    console.print()


@app.command(
    "kill",
    help=(
        "Close the process occupying a port.\n\n"
        "Shows the affected process and asks for confirmation before acting.\n"
        "Use --force to send SIGKILL instead of SIGTERM.\n"
        "Use --yes to skip confirmation (useful in scripts).\n\n"
        "Examples:\n\n"
        "  portctl kill 3000\n"
        "  portctl kill 8080 --force\n"
        "  portctl kill 5433 --yes"
    ),
)
def cmd_kill(
    port: int = typer.Argument(..., help="Port number to close"),
    force: bool = typer.Option(False, "--force", "-f", help="Use SIGKILL instead of SIGTERM"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Don't ask for confirmation"),
):
    ports = get_open_ports(filter_port=port)
    if not ports:
        console.print(f"[yellow]⚠[/]  No process found on port [bold]{port}[/]")
        raise typer.Exit(1)

    console.print()
    console.print(build_table(ports))
    console.print()

    if not yes and not Confirm.ask(f"  [bold red]Close process(es) on port {port}?[/]", default=False):
        console.print("[bright_black]  Cancelled.[/]")
        return

    sig_label = "[red]SIGKILL[/]" if force else "[yellow]SIGTERM[/]"
    console.print(f"  Sending {sig_label} to port [bold]{port}[/]...", end=" ")

    if kill_port(port, force=force):
        console.print("[bold green]✓ Closed[/]")
    else:
        console.print("[bold red]✗ Error[/] [bright_black](sufficient permissions?)[/]")


@app.command(
    "interactive",
    help=(
        "Interactive menu to inspect and close ports.\n\n"
        "Shows ports in LISTEN state and allows selecting them\n"
        "by row number or port number directly.\n"
        "Multiple selections can be made by separating with commas.\n\n"
        "Selection examples within the menu:\n\n"
        "  3          → close row 3\n"
        "  8080       → close port 8080\n"
        "  1,3,5      → close rows 1, 3, and 5\n"
        "  q          → quit"
    ),
)
def cmd_interactive():
    while True:
        listen_ports = get_open_ports(filter_state="LISTEN")

        if not listen_ports:
            console.print(Panel("[yellow]No ports in LISTEN state[/]", border_style="yellow"))
            return

        console.clear()
        console.print()
        console.print(
            Panel(
                "[bold white]🔌 portctl[/] [bright_black]—[/] [cyan]interactive mode[/]",
                border_style="bright_black",
                expand=False,
            )
        )
        console.print(build_table(listen_ports))
        console.print()
        console.print("[bright_black]  Select by row or port · multiple with commas · [white]q[/] to quit[/]")
        console.print()

        choice = Prompt.ask("  [bold cyan]>[/]").strip()

        if choice.lower() in ("q", "quit", "exit"):
            console.print("[bright_black]  Goodbye.[/]")
            break

        targets = []
        for part in choice.split(","):
            part = part.strip()
            if not part.isdigit():
                console.print(f"[red]  Invalid input:[/] {part!r}")
                continue
            num = int(part)
            if 1 <= num <= len(listen_ports):
                targets.append(listen_ports[num - 1])
            else:
                matches = [p for p in listen_ports if p["port"] == num]
                targets.extend(matches) if matches else console.print(f"[red]  Not found:[/] {num}")

        if not targets:
            continue

        console.print()
        for t in targets:
            console.print(f"  → Port [bold yellow]{t['port']}[/]  PID [magenta]{t['pid']}[/]  [white]{t['name']}[/]")
        console.print()

        force = Confirm.ask("  Use SIGKILL (force close)?", default=False)
        if Confirm.ask(f"  [bold red]Close {len(targets)} process(es)?[/]", default=False):
            for t in targets:
                icon = "[green]✓[/]" if kill_port(t["port"], force=force) else "[red]✗[/]"
                console.print(f"  {icon} Port [bold]{t['port']}[/]")
        else:
            console.print("[bright_black]  Cancelled.[/]")

        console.print()
        Prompt.ask("  [bright_black]Press Enter to continue[/]", default="")


if __name__ == "__main__":
    app()
