from buffer_protocol import BufferProtocol, BUFFER_T_BEGIN, BUFFER_T_END

import asyncio
import pytest

class SerialProtocol:
    def __init__(self):
        self.r = asyncio.Queue()
        self.w = asyncio.Queue()

    async def read(self) -> int:
        buf = await self.r.get()
        self.r.task_done()
        return buf

    async def write(self, ch: int):
        return await self.w.put(ch)

    def available(self):
        return not self.r.empty()

async def read_from_queue(q: asyncio.Queue) -> list:
    x = []
    while not q.empty():
        x.append(await q.get())
    return x

async def write_to_queue(q: asyncio.Queue, b: list):
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
        assert await bp.read() == BUFFER_T_END

@pytest.mark.asyncio
async def test_read_write_corrupt_bytes():
    sp = SerialProtocol()
    bp = BufferProtocol(sp)
    for i in range(26):
        await bp.begin()
        for j in range(5):
            await bp.write(i + ord('a'))
        await bp.end()
    buffer = await read_from_queue(sp.w)
    while len(buffer) > 0:
        await write_to_queue(sp.r, buffer)
        read_list = []
        while sp.available():
            data = await bp.read()
            if data > 0:
                read_list.append(data)
        assert len(read_list) % 5 == 0
        for j in range(0, len(read_list), 5):
            for k in range(1, 5):
                assert read_list[j + k] == read_list[j]
        buffer = buffer[1:]

@pytest.mark.asyncio
async def test_should_end_transaction():
    sp = SerialProtocol()
    bp = BufferProtocol(sp)
    assert sp.available() == False
    for _ in range(5):
        await bp.begin()
        await bp.end()
    await write_to_queue(sp.r, await read_from_queue(sp.w))
    for i in range(5):
        assert await bp.read() == BUFFER_T_BEGIN
        assert await bp.read() == BUFFER_T_END
    assert sp.available() == False
    await write_to_queue(sp.r, [None])
    assert await bp.read() is None

@pytest.mark.asyncio
async def test_all_bytes():
    sp = SerialProtocol()
    bp = BufferProtocol(sp)
    await bp.begin()
    for i in range(256):
        await bp.write(i)
    await bp.end()
    await write_to_queue(sp.r, await read_from_queue(sp.w))
    assert await bp.read() == BUFFER_T_BEGIN
    for i in range(256):
        assert await bp.read() == i
    assert await bp.read() == BUFFER_T_END
    assert sp.available() == False

@pytest.mark.asyncio
async def test_all_bytes_interrupt():
    sp = SerialProtocol()
    bp = BufferProtocol(sp)
    await bp.begin()
    for i in range(256):
        await bp.write(i)
    await bp.end()
    data = await read_from_queue(sp.w)
    data[2] = None
    await write_to_queue(sp.r, data)
    assert await bp.read() == BUFFER_T_BEGIN
    for i in range(256):
        ch = await bp.read()
        assert ch == i or ch is None
        if ch is None:
            return
    assert await bp.read() == BUFFER_T_END
    assert sp.available() == False