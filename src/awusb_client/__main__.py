"""Interface for ``python -m awusb_client``."""

from collections.abc import Sequence

import typer

from . import __version__
from .client import attach_device, list_devices
from .server import CommandServer
from .usbdevice import get_devices

__all__ = ["main"]

app = typer.Typer()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"awusb-client {__version__}")
        raise typer.Exit()


@app.callback()
def common_options(
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Common options for all commands."""
    pass


@app.command()
def server() -> None:
    """Start the USB sharing server."""
    server = CommandServer()
    server.start()


@app.command()
def list(
    local: bool = typer.Option(
        False,
        "--local",
        "-l",
        help="List local USB devices instead of querying the server",
    ),
) -> None:
    """List the available USB devices from the server."""
    if local:
        from .usbdevice import get_devices

        devices = get_devices()
    else:
        devices = list_devices()

    for device in devices:
        print(device)


def main(args: Sequence[str] | None = None) -> None:
    """Argument parser for the CLI."""
    app()


if __name__ == "__main__":
    main()
