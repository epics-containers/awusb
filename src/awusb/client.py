import logging
import socket

from pydantic import TypeAdapter

from .models import (
    AttachRequest,
    AttachResponse,
    ErrorResponse,
    ListRequest,
    ListResponse,
)
from .usbdevice import UsbDevice
from .utility import run_command

logger = logging.getLogger(__name__)


def send_request(request, server_host="localhost", server_port=5000):
    """
    Send a request to the server and return the response.

    Args:
        request: The request object to send
        server_host: Server hostname or IP address
        server_port: Server port number

    Returns:
        The response object from the server

    Raises:
        RuntimeError: If the server returns an error response
    """
    logger.debug(f"Connecting to server at {server_host}:{server_port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_host, server_port))
        logger.debug(f"Sending request: {request.command}")
        sock.sendall(request.model_dump_json().encode("utf-8"))

        response = sock.recv(4096).decode("utf-8")
        logger.debug("Received response from server")
        # Parse response using TypeAdapter to handle union types
        response_adapter = TypeAdapter(ListResponse | AttachResponse | ErrorResponse)
        decoded = response_adapter.validate_json(response)

        if isinstance(decoded, ErrorResponse):
            logger.error(f"Server returned error: {decoded.message}")
            raise RuntimeError(f"Server error: {decoded.message}")

        logger.debug(f"Request successful: {request.command}")
        return decoded


def list_devices(server_host="localhost", server_port=5000) -> list[UsbDevice]:
    """
    Request list of available USB devices from the server.

    Args:
        server_host: Server hostname or IP address
        server_port: Server port number

    Returns:
        List of UsbDevice instances
    """
    logger.info(f"Requesting device list from {server_host}:{server_port}")
    request = ListRequest()
    response = send_request(request, server_host, server_port)
    logger.info(f"Retrieved {len(response.data)} devices")
    return response.data


def attach_detach_device(
    args: AttachRequest, server_host="localhost", server_port=5000, detach: bool = False
) -> UsbDevice:
    """
    Request to attach or detach a USB device from the server.

    Args:
        id: ID of the device to attach
        server_host: Server hostname or IP address
        server_port: Server port number

    Returns:
        The device that was attached, or detached
    """
    action = "detach" if detach else "attach"
    logger.info(f"Requesting {action} from {server_host}:{server_port}")
    response = send_request(args, server_host, server_port)

    if not detach:
        logger.info(f"Attaching device {response.data.bus_id} to local system")
        run_command(
            [
                "sudo",
                "usbip",
                "attach",
                "-r",
                server_host,
                "-b",
                response.data.bus_id,
            ]
        )
        logger.info(f"Device attached successfully: {response.data.description}")
    else:
        logger.info(f"Device detached: {response.data.description}")

    return response.data
