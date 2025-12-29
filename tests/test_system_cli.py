"""
System-level CLI tests using real command execution with mocked USB/IP.

These tests use the same subprocess mocks as test_system_integration
but test the CLI commands directly.
"""

from unittest.mock import patch

from typer.testing import CliRunner

from usb_remote.__main__ import app
from usb_remote.config import UsbRemoteConfig

runner = CliRunner()


class TestSystemCLI:
    """Test CLI commands with system-level mocks."""

    def test_list_command(self, mock_subprocess_run, server_port, server_instance):
        """Test the list command with mocked USB devices."""
        # Mock config to use our test server
        test_config = UsbRemoteConfig(
            servers=["127.0.0.1"], server_port=server_port, timeout=0.5
        )
        with patch("usb_remote.config.get_config", return_value=test_config):
            result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Should show devices from the mock
        assert "2e8a:000a" in result.stdout
        assert "Raspberry Pi" in result.stdout

    def test_list_with_server_option(
        self, mock_subprocess_run, server_port, server_instance
    ):
        """Test list command with explicit server."""
        test_config = UsbRemoteConfig(server_port=server_port, timeout=0.5)
        with patch("usb_remote.config.get_config", return_value=test_config):
            result = runner.invoke(app, ["list", "--host", "127.0.0.1"])

        assert result.exit_code == 0, f"Command failed: {result.stdout}"
        assert "2e8a:000a" in result.stdout

    def test_attach_command_with_busid(
        self, mock_subprocess_run, server_port, server_instance
    ):
        """Test attach command with bus ID."""
        test_config = UsbRemoteConfig(server_port=server_port, timeout=0.5)
        with patch("usb_remote.config.get_config", return_value=test_config):
            result = runner.invoke(
                app, ["attach", "--bus", "1-1.1", "--host", "127.0.0.1"]
            )

        # The command should succeed
        assert result.exit_code == 0

        # Verify subprocess.run was called for bind and attach
        bind_calls = [
            call
            for call in mock_subprocess_run.call_args_list
            if len(call.args) > 0
            and len(call.args[0]) > 2
            and call.args[0][0] == "sudo"
            and call.args[0][1] == "usbip"
            and call.args[0][2] == "bind"
        ]
        assert len(bind_calls) >= 1, "Should have called usbip bind"

    def test_attach_command_with_vendor_product(
        self, mock_subprocess_run, server_port, server_instance
    ):
        """Test attach command with vendor and product IDs."""
        test_config = UsbRemoteConfig(server_port=server_port, timeout=0.5)
        with patch("usb_remote.config.get_config", return_value=test_config):
            result = runner.invoke(
                app, ["attach", "--id", "2e8a:000a", "--host", "127.0.0.1"]
            )

        # The command should succeed
        assert result.exit_code == 0, f"Command failed: {result.stdout}"

    def test_detach_command(self, mock_subprocess_run, server_port, server_instance):
        """Test detach command after attaching a device."""
        test_config = UsbRemoteConfig(server_port=server_port, timeout=0.5)
        with patch("usb_remote.config.get_config", return_value=test_config):
            # First attach a device
            attach_result = runner.invoke(
                app, ["attach", "--bus", "1-1.1", "--host", "127.0.0.1"]
            )
            assert attach_result.exit_code == 0

            # Now detach it
            detach_result = runner.invoke(
                app, ["detach", "--bus", "1-1.1", "--host", "127.0.0.1"]
            )

        # The command should succeed
        assert detach_result.exit_code == 0

        # Verify subprocess.run was called for unbind and detach
        unbind_calls = [
            call
            for call in mock_subprocess_run.call_args_list
            if len(call.args) > 0
            and len(call.args[0]) > 2
            and call.args[0][0] == "sudo"
            and call.args[0][1] == "usbip"
            and call.args[0][2] == "unbind"
        ]
        assert len(unbind_calls) >= 1, "Should have called usbip unbind"

        detach_calls = [
            call
            for call in mock_subprocess_run.call_args_list
            if len(call.args) > 0
            and len(call.args[0]) > 2
            and call.args[0][0] == "sudo"
            and call.args[0][1] == "usbip"
            and call.args[0][2] == "detach"
        ]
        assert len(detach_calls) >= 1, "Should have called usbip detach"

    def test_list_ports_command(
        self, mock_subprocess_run, server_port, server_instance
    ):
        """Test ports command."""
        test_config = UsbRemoteConfig(server_port=server_port, timeout=0.5)
        with patch("usb_remote.config.get_config", return_value=test_config):
            # First attach a device so there's something to list
            attach_result = runner.invoke(
                app, ["attach", "--bus", "1-1.1", "--host", "127.0.0.1"]
            )
            assert attach_result.exit_code == 0

            # Now list ports
            result = runner.invoke(app, ["ports"])

        assert result.exit_code == 0, f"Command failed: {result.stdout}"
        # Should show the attached device
        assert "Port" in result.stdout

    def test_find_command(self, mock_subprocess_run, server_port, server_instance):
        """Test find command with vendor/product IDs."""
        test_config = UsbRemoteConfig(server_port=server_port, timeout=0.5)
        with patch("usb_remote.config.get_config", return_value=test_config):
            result = runner.invoke(
                app, ["find", "--id", "2e8a:000a", "--host", "127.0.0.1"]
            )

        assert result.exit_code == 0, f"Command failed: {result.stdout}"
        assert "1-1.1" in result.stdout
        assert "2e8a:000a" in result.stdout
