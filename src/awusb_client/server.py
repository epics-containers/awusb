import socket
import threading


class CommandServer:
    def __init__(self, host: str = "localhost", port: int = 5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def handle_list(self) -> str:
        """Handle the 'list' command."""
        # TODO: Implement list logic
        return "List of devices"

    def handle_attach(
        self,
        id: str | None = None,
        bus: str | None = None,
        serial_no: str | None = None,
    ) -> bool:
        """Handle the 'attach' command with optional arguments."""
        # TODO: Implement attach logic
        return True

    def handle_client(self, client_socket: socket.socket, address):
        """Handle individual client connections."""
        try:
            data = client_socket.recv(1024).decode("utf-8")
            command_parts = data.strip().split()

            if not command_parts:
                client_socket.sendall(b"ERROR: Empty command\n")
                return

            command = command_parts[0]

            if command == "list":
                result = self.handle_list()
                client_socket.sendall(result.encode("utf-8") + b"\n")

            elif command == "attach":
                kwargs = {}
                for part in command_parts[1:]:
                    if ":" in part:
                        key, value = part.split(":", 1)
                        kwargs[key] = value

                result = self.handle_attach(**kwargs)
                response = "SUCCESS" if result else "FAILURE"
                client_socket.sendall(response.encode("utf-8") + b"\n")

            else:
                client_socket.sendall(b"ERROR: Unknown command\n")

        except Exception as e:
            client_socket.sendall(f"ERROR: {str(e)}\n".encode("utf-8"))

        finally:
            client_socket.close()

    def start(self):
        """Start the server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True

        print(f"Server listening on {self.host}:{self.port}")

        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, address)
                )
                client_thread.start()
            except OSError:
                break

    def stop(self):
        """Stop the server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
