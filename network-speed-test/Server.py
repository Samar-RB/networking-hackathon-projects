import socket
import threading
import time
import math
from utils import encode_offer_packet, decode_request_packet, encode_payload_packet
from constants import *

class NetworkServer:
    def __init__(self, udp_listen_port=DEFAULT_UDP_PORT, tcp_listen_port=DEFAULT_TCP_PORT):
        self.udp_listen_port = udp_listen_port
        self.tcp_listen_port = tcp_listen_port
        self.server_running = True

        #  UDP socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.bind(("", udp_listen_port))

        # TCP socket
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind(("", tcp_listen_port))
        self.tcp_socket.listen(5)

    def start(self):
        print(f"Server started, listening on IP address {self.get_local_ip()}")
        threading.Thread(target=self.broadcast_offers, daemon=True).start()
        threading.Thread(target=self.handle_tcp_connections, daemon=True).start()
        threading.Thread(target=self.handle_udp_requests, daemon=True).start()

        try:
            while self.server_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down server...")
            self.server_running = False

    def get_local_ip(self):
        """Retrieve the server's local IP address."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]

    def broadcast_offers(self):
        """Broadcast server availability to clients."""
        offer_packet = encode_offer_packet(self.udp_listen_port, self.tcp_listen_port)
        while self.server_running:
            self.udp_socket.sendto(offer_packet, ("255.255.255.255", UDP_BROADCAST_PORT))
            time.sleep(1)

    def handle_tcp_connections(self):
        """Accept and manage TCP connections from clients."""
        while self.server_running:
            client_socket, client_address = self.tcp_socket.accept()
            print(f"Accepted TCP connection from {client_address}")
            threading.Thread(target=self.tcp_transfer, args=(client_socket,), daemon=True).start()

    def tcp_transfer(self, client_socket):
        """Handle TCP data transfer for a single client."""
        try:
            file_size = int(client_socket.recv(BUFFER_SIZE).strip())
            print(f"Received TCP request for {file_size} bytes.")
            bytes_sent = 0
            while bytes_sent < file_size:
                chunk = b"x" * 1
                client_socket.sendall(chunk)
                bytes_sent += len(chunk)
                print(f"TCP transfer: Sent {bytes_sent}/{file_size} bytes.")
        except Exception as e:
            print(f"Error during TCP transfer: {e}")
        finally:
            client_socket.close()



    def handle_udp_requests(self):
        """Handle incoming UDP requests from clients."""
        while self.server_running:
            try:
                data, client_address = self.udp_socket.recvfrom(BUFFER_SIZE)
                print(f"Received UDP request from {client_address}")
                cookie, type, file_total_size = decode_request_packet(data)

                if cookie == MAGIC_COOKIE and type == MESSAGE_TYPE_REQUEST:
                    threading.Thread(
                        target=self.udp_transfer, args=(client_address, file_total_size), daemon=True
                    ).start()
            except Exception as error:
                print(f"Error handling UDP request: {error}")

    def udp_transfer(self, client_address, file_size):
        """Handle UDP data transfer for a single client."""
        total_segments = math.ceil(file_size / BUFFER_SIZE)
        print(f"Starting UDP transfer to {client_address}, total segments: {total_segments}")
        for segment in range(total_segments):
            payload = b"x" * 1
            packet = encode_payload_packet(total_segments, segment + 1) + payload
            self.udp_socket.sendto(packet, client_address)
            print(f"Sent UDP segment {segment + 1}/{total_segments} to {client_address}")
            time.sleep(0.001)


if __name__ == "__main__":
    server = NetworkServer()
    server.start()
