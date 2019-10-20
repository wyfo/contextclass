from contextvars import copy_context
from functools import wraps

from pytest import hookimpl


@hookimpl
def pytest_pyfunc_call(pyfuncitem):
    """run tests into separated context"""

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            return copy_context().run(func, *args, **kwargs)

        return inner

    pyfuncitem.obj = wrapper(pyfuncitem.obj)
