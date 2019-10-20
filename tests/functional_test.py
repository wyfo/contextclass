import asyncio

from pytest import mark

from contextclasses import contextclass


@mark.asyncio
async def test_use_case():
    """Functional test"""

    @contextclass
    class Ctx:
        n: int

    async def use_ctx(n: int):
        Ctx.n = n
        await asyncio.sleep(0)  # switch context
        return Ctx.n

    values = [*range(5)]
    result = await asyncio.gather(*(use_ctx(n) for n in values))
    # despite context switching, context is preserved
    assert result == values
