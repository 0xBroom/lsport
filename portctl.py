#!/usr/local/bin/python3
"""
portctl - Consulta y cierra puertos abiertos rápidamente
"""

__version__ = "0.1.0"

import os
import signal
import psutil
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich import box
from typing import Optional, List

VALID_STATES = ('LISTEN', 'ESTABLISHED', 'CLOSE_WAIT')

app = typer.Typer(
    help=(
        "🔌 portctl — Consulta y cierra puertos abiertos en macOS.\n\n"
        "Comandos disponibles:\n\n"
        "  list          Lista todos los puertos abiertos (TCP).\n"
        "                Usa -s/--state para filtrar por estado.\n\n"
        "  kill <puerto> Termina el proceso que ocupa ese puerto.\n"
        "                Pide confirmación antes de actuar.\n\n"
        "  interactive   Menú interactivo: selecciona y cierra puertos\n"
        "                con navegación por número de fila o puerto.\n\n"
        "Estados disponibles para -s/--state:\n\n"
        "  listen        Puertos esperando conexiones entrantes.\n"
        "  established   Conexiones activas en este momento.\n"
        "  close_wait    Conexiones cerrándose por el lado remoto."
    ),
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def get_open_ports(filter_port: Optional[int] = None, filter_state: Optional[str] = None) -> List[dict]:
    ports = []
    seen = set()
    state_filter = filter_state.upper() if filter_state else None

    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            conns = proc.net_connections(kind='inet')
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
                ports.append({
                    'port': port,
                    'pid': proc.pid,
                    'name': proc.info['name'] or '?',
                    'user': proc.info['username'] or '?',
                    'status': conn.status,
                    'proto': 'TCP',
                    'addr': str(conn.laddr.ip),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    ports.sort(key=lambda x: x['port'])
    return ports


def status_color(status: str) -> str:
    return {'LISTEN': 'green', 'ESTABLISHED': 'cyan', 'CLOSE_WAIT': 'yellow'}.get(status, 'white')


def build_table(ports: List[dict], selected: Optional[set] = None) -> Table:
    table = Table(
        box=box.ROUNDED,
        border_style="bright_black",
        header_style="bold white on #1a1a2e",
        show_lines=False,
        pad_edge=True,
    )
    table.add_column("#",         style="bright_black", width=4,  justify="right")
    table.add_column("Puerto",    style="bold yellow",  width=8,  justify="right")
    table.add_column("Proto",     style="blue",         width=6)
    table.add_column("Dirección", style="bright_black", width=16)
    table.add_column("Estado",                          width=13)
    table.add_column("PID",       style="magenta",      width=7,  justify="right")
    table.add_column("Proceso",   style="white",        width=20)
    table.add_column("Usuario",   style="bright_black", width=12)

    for i, p in enumerate(ports, 1):
        color = status_color(p['status'])
        sel_mark = "✓ " if selected and p['port'] in selected else "  "
        row_style = "on #1c1c1c" if selected and p['port'] in selected else ""
        table.add_row(
            f"{sel_mark}{i}",
            str(p['port']),
            p['proto'],
            p['addr'],
            Text(p['status'], style=f"bold {color}"),
            str(p['pid']),
            p['name'][:20],
            p['user'][:12],
            style=row_style,
        )
    return table


def kill_port(port: int, force: bool = False) -> bool:
    killed = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.net_connections(kind='inet'):
                if conn.laddr and conn.laddr.port == port:
                    os.kill(proc.pid, signal.SIGKILL if force else signal.SIGTERM)
                    killed.append(proc.pid)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, ProcessLookupError):
            continue
    return len(killed) > 0


# ─── Comandos ───────────────────────────────────────────────────────────────

@app.command(
    "list",
    help=(
        "Lista los puertos abiertos del sistema.\n\n"
        "Sin opciones muestra todos (LISTEN, ESTABLISHED, CLOSE_WAIT).\n"
        "Usa -s/--state para filtrar por un estado concreto.\n\n"
        "Ejemplos:\n\n"
        "  portctl list\n"
        "  portctl list -s listen\n"
        "  portctl list -s established\n"
        "  portctl list -s close_wait"
    ),
)
def cmd_list(
    state: Optional[str] = typer.Option(
        None, "--state", "-s",
        help="Filtra por estado: listen | established | close_wait",
        metavar="ESTADO",
    ),
):
    if state and state.upper() not in VALID_STATES:
        console.print(
            f"[red]✗[/]  Estado desconocido: [bold]{state}[/]\n"
            f"    Valores válidos: [cyan]listen[/] · [cyan]established[/] · [cyan]close_wait[/]"
        )
        raise typer.Exit(1)

    ports = get_open_ports(filter_state=state)

    if not ports:
        hint = f" con estado [bold]{state.upper()}[/]" if state else ""
        console.print(Panel(f"[yellow]No se encontraron puertos abiertos[/]{hint}", border_style="yellow"))
        return

    label = f"[bold white]🔌 portctl[/] [bright_black]—[/] [cyan]{len(ports)} puertos encontrados[/]"
    if state:
        label += f"  [bright_black]({state.upper()})[/]"

    console.print()
    console.print(Panel(label, border_style="bright_black", expand=False))
    console.print(build_table(ports))
    console.print()


@app.command(
    "kill",
    help=(
        "Cierra el proceso que ocupa un puerto.\n\n"
        "Muestra el proceso afectado y pide confirmación antes de actuar.\n"
        "Usa --force para enviar SIGKILL en vez de SIGTERM.\n"
        "Usa --yes para omitir la confirmación (útil en scripts).\n\n"
        "Ejemplos:\n\n"
        "  portctl kill 3000\n"
        "  portctl kill 8080 --force\n"
        "  portctl kill 5433 --yes"
    ),
)
def cmd_kill(
    port:  int  = typer.Argument(..., help="Número de puerto a cerrar"),
    force: bool = typer.Option(False, "--force", "-f", help="Usar SIGKILL en vez de SIGTERM"),
    yes:   bool = typer.Option(False, "--yes",   "-y", help="No pedir confirmación"),
):
    ports = get_open_ports(filter_port=port)
    if not ports:
        console.print(f"[yellow]⚠[/]  No hay ningún proceso en el puerto [bold]{port}[/]")
        raise typer.Exit(1)

    console.print()
    console.print(build_table(ports))
    console.print()

    if not yes:
        if not Confirm.ask(f"  [bold red]¿Cerrar proceso(s) en el puerto {port}?[/]", default=False):
            console.print("[bright_black]  Cancelado.[/]")
            return

    sig_label = "[red]SIGKILL[/]" if force else "[yellow]SIGTERM[/]"
    console.print(f"  Enviando {sig_label} al puerto [bold]{port}[/]...", end=" ")

    if kill_port(port, force=force):
        console.print("[bold green]✓ Cerrado[/]")
    else:
        console.print("[bold red]✗ Error[/] [bright_black](¿permisos suficientes?)[/]")


@app.command(
    "interactive",
    help=(
        "Menú interactivo para inspeccionar y cerrar puertos.\n\n"
        "Muestra los puertos en LISTEN y permite seleccionarlos\n"
        "por número de fila o por número de puerto directamente.\n"
        "Se pueden seleccionar varios a la vez separándolos con comas.\n\n"
        "Ejemplos de selección dentro del menú:\n\n"
        "  3          → cierra la fila 3\n"
        "  8080       → cierra el puerto 8080\n"
        "  1,3,5      → cierra las filas 1, 3 y 5\n"
        "  q          → salir"
    ),
)
def cmd_interactive():
    while True:
        listen_ports = get_open_ports(filter_state='LISTEN')

        if not listen_ports:
            console.print(Panel("[yellow]No hay puertos en estado LISTEN[/]", border_style="yellow"))
            return

        console.clear()
        console.print()
        console.print(Panel(
            "[bold white]🔌 portctl[/] [bright_black]—[/] [cyan]modo interactivo[/]",
            border_style="bright_black",
            expand=False,
        ))
        console.print(build_table(listen_ports))
        console.print()
        console.print("[bright_black]  Selecciona por fila o puerto · varios con comas · [white]q[/] para salir[/]")
        console.print()

        choice = Prompt.ask("  [bold cyan]>[/]").strip()

        if choice.lower() in ('q', 'quit', 'exit', 'salir'):
            console.print("[bright_black]  Hasta luego.[/]")
            break

        targets = []
        for part in choice.split(','):
            part = part.strip()
            if not part.isdigit():
                console.print(f"[red]  Entrada inválida:[/] {part!r}")
                continue
            num = int(part)
            if 1 <= num <= len(listen_ports):
                targets.append(listen_ports[num - 1])
            else:
                matches = [p for p in listen_ports if p['port'] == num]
                targets.extend(matches) if matches else console.print(f"[red]  No encontrado:[/] {num}")

        if not targets:
            continue

        console.print()
        for t in targets:
            console.print(f"  → Puerto [bold yellow]{t['port']}[/]  PID [magenta]{t['pid']}[/]  [white]{t['name']}[/]")
        console.print()

        force = Confirm.ask("  ¿Usar SIGKILL (forzar cierre)?", default=False)
        if Confirm.ask(f"  [bold red]¿Cerrar {len(targets)} proceso(s)?[/]", default=False):
            for t in targets:
                icon = "[green]✓[/]" if kill_port(t['port'], force=force) else "[red]✗[/]"
                console.print(f"  {icon} Puerto [bold]{t['port']}[/]")
        else:
            console.print("[bright_black]  Cancelado.[/]")

        console.print()
        Prompt.ask("  [bright_black]Pulsa Enter para continuar[/]", default="")


if __name__ == "__main__":
    app()
