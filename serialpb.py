#!/usr/bin/env python3
from struct import pack, unpack
from collections import deque

MAGIC_HEAD = 0xdead
MAGIC_NUMBER = 0xbeef
PACKET_SIZE = 32
CONTENT_SIZE = PACKET_SIZE - 6

def crc16(data: bytes):
    data = bytearray(data)
    poly = 0xA001
    crc = 0xFFFF
    for b in data:
        crc ^= (0xFF & b)
        for _ in range(0, 8):
            if (crc & 0x0001):
                crc = ((crc >> 1) & 0xFFFF) ^ poly
            else:
                crc = ((crc >> 1) & 0xFFFF)
    return crc

def peek_chunk(buffer: deque, sz: int) -> bytes:
    result = bytearray()
    for i in range(sz):
        result.append(buffer[i])
    return result

def pop_chunk(buffer: deque, sz: int):
    for _ in range(sz):
        buffer.popleft()

class SerialProtocol(object):

    def __init__(self):
        self.buffer = deque()

    def on_packet_recv(self, data: bytes):
        self.buffer.extend(data)
        while len(self.buffer) >= PACKET_SIZE:
            chunk = peek_chunk(self.buffer, PACKET_SIZE)
            if unpack("<H", chunk[0:2])[0] != MAGIC_HEAD:
                self.buffer.popleft()
            else:
                pop_chunk(self.buffer, PACKET_SIZE)
                print(chunk)

    def send_packet(self, data: bytes) -> bytes:
        sz = len(data)
        result = bytearray()
        current_packet = bytearray()
        padding = 0 if sz % CONTENT_SIZE == 0 else CONTENT_SIZE - sz % CONTENT_SIZE
        data = bytearray(data)
        data.extend(bytes([0]) * (padding + 1))
        for (idx, ch) in enumerate(data):
            if idx % CONTENT_SIZE == 0:
                if idx != 0:
                    crc = crc16(current_packet)
                    result.extend(current_packet)
                    result.extend(pack("<H", crc))
                current_packet = bytearray()
                current_packet.extend(pack("<HH", MAGIC_HEAD, sz))
            current_packet.append(ch)
        return bytes(result)

protocol = SerialProtocol()
msg = protocol.send_packet(b"Hello, World!")
print(msg)
protocol.on_packet_recv(msg)
