import struct
from constants import *

def encode_offer_packet(udp_port: int, tcp_port: int) -> bytes:
    """Encode an offer packet."""
    return struct.pack('!IbHH', MAGIC_COOKIE, MESSAGE_TYPE_OFFER, udp_port, tcp_port)


def decode_offer_packet(data: bytes):
    """Decode an offer packet."""
    return struct.unpack('!IbHH', data)


def encode_request_packet(file_size: int) -> bytes:
    """Encode a request packet."""
    return struct.pack('!IbQ', MAGIC_COOKIE, MESSAGE_TYPE_REQUEST, file_size)


def decode_request_packet(data: bytes):
    """Decode a request packet."""
    return struct.unpack('!IbQ', data[:13])


def encode_payload_packet(total_segments: int, current_segment: int) -> bytes:
    """Encode a payload packet."""
    return struct.pack('!IbQQ', MAGIC_COOKIE, MESSAGE_TYPE_PAYLOAD, total_segments, current_segment)


def decode_payload_packet(data: bytes):
    """Decode a payload packet."""
    return struct.unpack('!IbQQ', data[:21])
