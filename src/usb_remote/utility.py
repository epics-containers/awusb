"""Utility functions for subprocess operations."""

import ipaddress
import logging
import socket
import subprocess

from usb_remote.config import SERVER_PORT, get_server_ranges, get_servers

logger = logging.getLogger(__name__)

# Server port constant (also defined in api.py to avoid circular import)


def get_host_list(host: str | None) -> list[str]:
    """Get list of server hosts from argument or config."""
    if host:
        servers = [host]
    else:
        servers = get_servers()
        # Scan server-ranges and add responsive servers
        ranges = get_server_ranges()
        for range_spec in ranges:
            servers.extend(_scan_ip_range(range_spec))
    if not servers:
        logger.warning("No servers configured, defaulting to localhost")
        servers = ["localhost"]
    return servers


def _scan_ip_range(range_spec: str) -> list[str]:
    """
    Scan an IP range and return addresses that are listening on SERVER_PORT.

    Args:
        range_spec: IP range specification like '192.168.1.30-192.168.1.40'

    Returns:
        List of IP addresses that are responsive on SERVER_PORT
    """
    responsive_servers = []

    try:
        # Parse the range specification
        if "-" in range_spec:
            start_ip_str, end_ip_str = range_spec.split("-", 1)
            start_ip = ipaddress.ip_address(start_ip_str.strip())
            end_ip = ipaddress.ip_address(end_ip_str.strip())

            logger.debug(f"Scanning IP range: {start_ip} - {end_ip}")

            # Ensure both IPs are the same version
            if start_ip.version != end_ip.version:
                logger.error(f"IP version mismatch in range: {range_spec}")
                return responsive_servers

            # Convert to integers for comparison
            start_int = int(start_ip)
            end_int = int(end_ip)

            # Ensure start <= end
            if start_int > end_int:
                logger.error(f"Invalid IP range (start > end): {range_spec}")
                return responsive_servers

            # Scan each IP in the range
            current_int = start_int
            while current_int <= end_int:
                current_ip = ipaddress.ip_address(current_int)
                ip_str = str(current_ip)
                if _is_port_open(ip_str, SERVER_PORT):
                    logger.info(f"Found server at {ip_str}:{SERVER_PORT}")
                    responsive_servers.append(ip_str)
                else:
                    logger.debug(f"No response from {ip_str}:{SERVER_PORT}")
                current_int += 1

    except ValueError as e:
        logger.error(f"Invalid IP range specification '{range_spec}': {e}")
    except Exception as e:
        logger.error(f"Error scanning IP range '{range_spec}': {e}")

    return responsive_servers


def _is_port_open(host: str, port: int, timeout: float = 0.1) -> bool:
    """
    Check if a port is open on a given host.

    Args:
        host: IP address or hostname
        port: Port number to check
        timeout: Connection timeout in seconds

    Returns:
        True if port is open, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except OSError:
        return False


def run_command(
    command: list[str],
    capture_output: bool = True,
    text: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess:
    """
    Run a command using subprocess.run with common defaults.

    Args:
        command: The command and its arguments as a list of strings
        capture_output: Whether to capture stdout and stderr
        text: Whether to return output as text (string) instead of bytes
        check: Whether to raise CalledProcessError on non-zero exit

    Returns:
        CompletedProcess instance containing the result

    Raises:
        CalledProcessError: If check=True and the command returns non-zero
    """
    try:
        logger.debug(f"Running command: {' '.join(command)}")
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=text,
            check=check,
        )
        logger.debug(f"Command completed with exit code {result.returncode}")
        return result
    except subprocess.CalledProcessError as e:
        cmd_str = " ".join(command)
        logger.error(f"Command '{cmd_str}' failed with exit code {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise RuntimeError(e.stderr) from e
