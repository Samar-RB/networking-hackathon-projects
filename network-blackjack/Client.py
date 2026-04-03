import socket
from utils import *
from constants import *


class NetworkClient:
    def start(self):
        rounds = int(input("Enter number of rounds: "))

        # ===== Listen for server offer =====
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(("", UDP_BROADCAST_PORT))

        data, addr = udp.recvfrom(1024)
        _, _, name, tcp_port = decode_offer_packet(data)

        print(f"Received offer from {name} at {addr[0]}")
        self.play(addr[0], tcp_port, rounds)

    def play(self, ip, port, rounds):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.sendall(encode_request(rounds))

        wins = 0

        for i in range(rounds):
            print(f"\n--- ROUND {i + 1} ---")
            if self.play_one_round(sock):
                wins += 1

        print(f"\nFinished playing {rounds} rounds, win rate: {wins / rounds:.2f}")
        sock.close()

    def play_one_round(self, sock):
        total = 0
        round_active = True   # 🔴 דגל קריטי

        while True:
            data = recv_exact(sock, 9)
            _, _, owner, result, rank, suit = decode_blackjack_payload(data)

            # ===== Player card =====
            if owner == 0 and result == 0:
                value = 11 if rank == 1 else min(rank, 10)
                total += value
                print(f"Player card: {rank}, total: {total}")

                # 🔥 Bust → הסיבוב נגמר, לא שולחים כלום
                if total > 21:
                    print("BUST ❌")
                    round_active = False
                    continue

                # ⛔ אם הסיבוב נגמר – לא מבקשים קלט
                if not round_active:
                    continue

                # ===== Player decision =====
                while True:
                    choice = input("Hit or Stand? ").strip().lower()
                    if choice == "hit":
                        sock.sendall(b"Hittt")
                        break
                    elif choice == "stand":
                        sock.sendall(b"Stand")
                        round_active = False
                        break
                    else:
                        print("❗ Please type 'hit' or 'stand'")

            # ===== Dealer card =====
            elif owner == 1:
                print(f"Dealer card: {rank}")

            # ===== Round result =====
            elif owner == 2:
                if result == 3:
                    print("YOU WIN ✅")
                    return True
                elif result == 2:
                    print("YOU LOSE ❌")
                    return False
                else:
                    print("TIE 🤝")
                    return False


def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise RuntimeError("Server closed connection")
        buf += chunk
    return buf


if __name__ == "__main__":
    NetworkClient().start()
