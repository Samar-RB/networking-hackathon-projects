import socket
import threading
import struct
import time
from constants import *


class NetworkClient:
    def __init__(self):
        self.running = True
        self.server_address = None
        self.server_udp_port = None
        self.server_tcp_port = None
        self.transfer_id = 0
        self.lock = threading.Lock()
        self.packet_id=0

    def start(self):
        """Start the client."""
        while self.running:
            print("Client started, listening for offer requests...")
            self.listen_for_offers()

    def listen_for_offers(self):
        """Listen for server offer packets."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind(("", UDP_BROADCAST_PORT))

            while self.running:
                try:
                    data, addr = udp_socket.recvfrom(1024)
                    cookie, msg_type, udp_port, tcp_port = struct.unpack('!IbHH', data)

                    if cookie == MAGIC_COOKIE and msg_type == OFFER_MESSAGE_TYPE:
                        self.server_address = addr[0]
                        self.server_udp_port = udp_port
                        self.server_tcp_port = tcp_port
                        print(f"Received offer from {self.server_address}")
                        self.prompt_user()
                        break
                except Exception as e:
                    print(f"Error receiving UDP data: {e}")

    def prompt_user(self):
        """Prompt user for file size and connections."""
        self.file_size = int(input("Enter file size (bytes): "))
        self.tcp_connections = int(input("Enter number of TCP connections: "))
        self.udp_connections = int(input("Enter number of UDP connections: "))
        self.run_speed_test()

    def run_speed_test(self):
        """Run the speed test."""
        tcp_threads = [
            threading.Thread(target=self.tcp_transfer) for i in range(self.tcp_connections)
        ]
        udp_threads = [
            threading.Thread(target=self.udp_transfer) for i in range(self.udp_connections)
        ]

        for t in tcp_threads + udp_threads:
            t.start()
        for t in tcp_threads + udp_threads:
            t.join()

        print("All transfers complete, listening to offer requests.")

    def tcp_transfer(self):
        """Perform a TCP transfer."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.server_address, self.server_tcp_port))
                sock.sendall(f"{self.file_size}\n".encode())

                start_time = time.time()
                bytes_received = 0

                while bytes_received < self.file_size:
                    data = sock.recv(BUFFER_SIZE)
                    if not data:
                        break
                    bytes_received += len(data)

                duration = time.time() - start_time
                speed = (bytes_received * 8) / duration
                print(
                    f"TCP transfer #{self.packet_id} finished, total time: {duration:.2f} seconds, "
                    f"total speed: {speed / 1e6:.2f} Mbps"
                )
                self.packet_id+=1
        except Exception as e:
            print(f"Error in TCP transfer #{self.packet_id}: {e}")

    def udp_transfer(self):
        """Perform a UDP transfer."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                request = struct.pack('!IbQ', MAGIC_COOKIE, REQUEST_MESSAGE_TYPE, self.file_size)
                sock.sendto(request, (self.server_address, self.server_udp_port))

                start_time = time.time()
                bytes_received = 0
                total_segments = 0
                received_segments = set()

                sock.settimeout(1.0)
                while True:
                    try:
                        data, _ = sock.recvfrom(2048)
                        header = data[:21]
                        cookie, msg_type, total_segments, segment_id = struct.unpack('!IbQQ', header)
                        received_segments.add(segment_id)
                        bytes_received += len(data)
                    except socket.timeout:
                        break

                duration = time.time() - start_time
                speed = (bytes_received * 8) / duration
                successful_packets = len(received_segments) / total_segments * 100 if total_segments else 0
                print(
                    f"UDP transfer #{self.packet_id} finished, total time: {duration:.2f} seconds, "
                    f"total speed: {speed / 1e6:.2f} Mbps, \npercentage of packets received successfully: {successful_packets:.2f}%"
                )
                self.packet_id+=1
        except Exception as e:
            print(f"Error in UDP transfer #{self.packet_id}: {e}")


if __name__ == "__main__":
    client = NetworkClient()
    client.start()
