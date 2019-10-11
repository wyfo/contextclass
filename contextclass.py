from contextvars import ContextVar, Token
from copy import deepcopy
from typing import Any, ContextManager, Dict, Mapping

context: ContextVar[Dict[str, Any]] = ContextVar("context", default={})


class ContextField:
    def __init__(self, name: str, default=...):
        self.name = name
        self.default = default

    def __get__(self, instance, owner):
        try:
            return context.get()[self.name]
        except KeyError:
            if self.default is not ...:
                default = deepcopy(self.default)
                context.get()[self.name] = default
                return default
            raise


class MetaContext(type):
    def __new__(mcs, name, bases, namespace):
        for field in namespace.get("__annotations__", {}):
            if field in namespace:
                namespace[field] = ContextField(field, namespace[field])
            else:
                namespace[field] = ContextField(field)
        return super().__new__(mcs, name, bases, namespace)

    def __setattr__(self, name, value):
        for cls in (self, *self.__bases__):
            if name in getattr(cls, "__annotations__", {}):
                context.get()[name] = value
                break
        else:
            super().__setattr__(name, value)


class Context(metaclass=MetaContext):
    pass


class ResetContext(ContextManager):
    def __init__(self, token: Token):
        self.token = token

    def __exit__(self, exc_type, exc_val, exc_tb):
        context.reset(self.token)


def init_context(ctx: Mapping[str, Any] = None, **kwargs) -> ResetContext:
    token = context.set({**(ctx or {}), **kwargs})
    return ResetContext(token)
