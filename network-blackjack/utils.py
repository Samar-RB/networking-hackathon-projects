import struct
from constants import *

# -------- UDP OFFER --------
# cookie | type | server_name(32 bytes) | tcp_port
def encode_offer_packet(server_name: str, tcp_port: int) -> bytes:
    name_bytes = server_name.encode()[:32]
    name_bytes += b'\x00' * (32 - len(name_bytes))
    return struct.pack(
        "!Ib32sH",
        MAGIC_COOKIE,
        MESSAGE_TYPE_OFFER,
        name_bytes,
        tcp_port
    )

def decode_offer_packet(data: bytes):
    cookie, msg_type, name_bytes, tcp_port = struct.unpack("!Ib32sH", data[:39])
    server_name = name_bytes.rstrip(b'\x00').decode()
    return cookie, msg_type, server_name, tcp_port


# -------- TCP REQUEST --------
def encode_request(rounds: int) -> bytes:
    return f"{rounds}\n".encode()

def decode_request(data: bytes) -> int:
    return int(data.decode().strip())


# -------- BLACKJACK PAYLOAD --------
# cookie | type | owner | result | rank | suit
# TOTAL SIZE = 9 bytes
def encode_blackjack_payload(owner, result, rank, suit):
    return struct.pack(
        "!IbBBBB",
        MAGIC_COOKIE,
        MESSAGE_TYPE_PAYLOAD,
        owner,   # 0=player, 1=dealer, 2=result
        result,  # 0=continue, 1=tie, 2=loss, 3=win
        rank,
        suit
    )

def decode_blackjack_payload(data):
    return struct.unpack("!IbBBBB", data[:9])
