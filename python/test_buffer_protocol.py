from buffer_protocol import BufferProtocol, BUFFER_T_BEGIN, BUFFER_T_END, BUFFER_END

import asyncio
import pytest

class SerialProtocol:
    def __init__(self):
        self.r = asyncio.Queue()
        self.w = asyncio.Queue()

    async def read(self) -> int:
        return await self.r.get()

    async def write(self, ch: int):
        return await self.w.put(ch)

async def read_from_queue(q: asyncio.Queue) -> bytes:
    x = bytearray()
    while not q.empty():
        x.append(await q.get())
    return bytes(x)

async def write_to_queue(q: asyncio.Queue, b: bytes):
    for ch in b:
        await q.put(ch)

@pytest.mark.asyncio
async def test_read_write_one_byte():
    sp = SerialProtocol()
    bp = BufferProtocol(sp)
    await bp.begin()
    await bp.write(0xff)
    await bp.end()
    await write_to_queue(sp.r, await read_from_queue(sp.w))
    assert await bp.read() == BUFFER_T_BEGIN
    assert await bp.read() == 0xff
    assert await bp.read() == BUFFER_T_END

@pytest.mark.asyncio
async def test_read_write_bytes():
    sp = SerialProtocol()
    bp = BufferProtocol(sp)
    for i in range(32):
        await bp.begin()
        for j in range(i + 1):
            await bp.write(j * 5)
        await bp.end()
    await write_to_queue(sp.r, await read_from_queue(sp.w))
    for i in range(32):
        assert await bp.read() == BUFFER_T_BEGIN
        for j in range(i + 1):
            assert await bp.read() == j * 5

@pytest.mark.asyncio
async def test_read_write_corrupt_bytes():
    sp = SerialProtocol()
    bp = BufferProtocol(sp)
    for i in range(26):
        await bp.begin()
        for j in range(i + 1):
            await bp.write(j + ord('a'))
        await bp.end()
    buffer = await read_from_queue(sp.w)
    while len(buffer) > 0:
        write_to_queue(sp.r, buffer)
        buffer = buffer[1:]
