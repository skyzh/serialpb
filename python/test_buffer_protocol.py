from buffer_protocol import BufferProtocol

import asyncio
import pytest

async def say(what, when):
    await asyncio.sleep(when)
    return what

@pytest.fixture
def sp():
    return SerialProtocol()

@pytest.mark.asyncio
async def test_say(sp):
    bp = BufferProtocol(sp)
