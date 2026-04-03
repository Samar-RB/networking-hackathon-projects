import socket
import threading
import random
import time
from utils import *
from constants import *

SERVER_NAME = "PerfectBlackjackServer"


class NetworkServer:
    def __init__(self):
        # UDP socket (offers)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.bind(("", 0))

        # TCP socket (game)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(("", DEFAULT_TCP_PORT))
        self.tcp_socket.listen(5)

    def start(self):
        print(f"Server started, listening on IP address {self.get_ip()}")
        threading.Thread(target=self.broadcast_offers, daemon=True).start()

        while True:
            client, addr = self.tcp_socket.accept()
            print(f"Client connected from {addr}")
            threading.Thread(
                target=self.handle_client, args=(client,), daemon=True
            ).start()

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def broadcast_offers(self):
        packet = encode_offer_packet(SERVER_NAME, DEFAULT_TCP_PORT)
        while True:
            self.udp_socket.sendto(packet, ("255.255.255.255", UDP_BROADCAST_PORT))
            time.sleep(1)

    # ================= BLACKJACK =================

    def handle_client(self, sock):
        try:
            rounds = decode_request(sock.recv(BUFFER_SIZE))
            print(f"Client requested {rounds} rounds")

            for _ in range(rounds):
                self.play_round(sock)

            sock.close()
            print("Client disconnected")

        except Exception as e:
            print("Error:", e)
            sock.close()

    def play_round(self, sock):
        deck = [(r, s) for r in range(1, 14) for s in range(4)]
        random.shuffle(deck)

        def value(r):
            return 11 if r == 1 else min(r, 10)

        # ---- Player initial cards ----
        player_cards = [deck.pop(), deck.pop()]
        player_total = sum(value(r) for r, _ in player_cards)

        for r, s in player_cards:
            sock.sendall(encode_blackjack_payload(0, 0, r, s))

        # ---- Player turn ----
        while True:
            decision_bytes = sock.recv(5)
            if not decision_bytes:
                return

            decision = decision_bytes.decode()

            if decision == "Hittt":
                r, s = deck.pop()
                player_total += value(r)
                sock.sendall(encode_blackjack_payload(0, 0, r, s))

                if player_total > 21:
                    sock.sendall(encode_blackjack_payload(2, 2, 0, 0))
                    return

            elif decision == "Stand":
                break

        # ---- Dealer turn ----
        dealer_cards = [deck.pop(), deck.pop()]
        dealer_total = sum(value(r) for r, _ in dealer_cards)

        for r, s in dealer_cards:
            sock.sendall(encode_blackjack_payload(1, 0, r, s))

        while dealer_total < 17:
            r, s = deck.pop()
            dealer_total += value(r)
            sock.sendall(encode_blackjack_payload(1, 0, r, s))

        # ---- Result ----
        if dealer_total > 21 or player_total > dealer_total:
            sock.sendall(encode_blackjack_payload(2, 3, 0, 0))  # WIN
        elif player_total == dealer_total:
            sock.sendall(encode_blackjack_payload(2, 1, 0, 0))  # TIE
        else:
            sock.sendall(encode_blackjack_payload(2, 2, 0, 0))  # LOSS


if __name__ == "__main__":
    NetworkServer().start()
