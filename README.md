# contextclasses - Context classes

Context classes provide a typed interface over a [context variable](https://docs.python.org/3/library/contextvars.html#contextvars.ContextVar) dictionary.
It can be used for example to reproduce Flask (thread-local) ["global" context](https://flask.palletsprojects.com/en/1.1.x/appcontext/) in an async web framework.

# Example

```python
import asyncio
from contextclasses import contextclass


async def test_use_case():
    @contextclass
    class Ctx:
        n: int

    async def use_ctx(n: int):
        Ctx.n = n
        await asyncio.sleep(0) # switch context
        return Ctx.n

    values = [*range(5)]
    result = await asyncio.gather(*(use_ctx(n) for n in values))
    assert result == values
```

For more examples, please look at the [tests](tests)