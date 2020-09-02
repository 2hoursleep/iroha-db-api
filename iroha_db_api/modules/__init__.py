from rich.console import Console
from rich.panel import Panel
import click
import os

console = Console()
style = "bold on black"


def _print(msg):
    # panel = Panel(f"{msg}", style="bold white on red", expand=False)
    return console.print(f"{msg}", style=style, justify="center")
