from contextvars import ContextVar, Token
from copy import deepcopy
from inspect import isclass
from typing import (Any, Callable, ContextManager, Dict, Mapping, TypeVar,
                    cast, overload)

ContextDict = ContextVar[Dict[str, Any]]
default_context: ContextDict = ContextVar("default_context", default={})


class ContextField:
    def __init__(self, name: str, default=...):
        self.name = name
        self.default = default

    def __get__(self, instance, owner):
        try:
            return instance.__context__.get()[self.name]
        except KeyError:
            if self.default is not ...:
                default = deepcopy(self.default)
                instance.__context__.get()[self.name] = default
                return default
            raise KeyError(self.name)

    def __set__(self, instance, value):
        instance.__context__.get()[self.name] = value

    def __delete__(self, instance):
        del instance.__context__.get()[self.name]


class MetaContextClass(type):
    __context__: ContextDict


Cls = TypeVar("Cls", bound=type)


def iscontextclass(cls: type) -> bool:
    return isinstance(cls, MetaContextClass)


@overload
def contextclass(cls: Cls) -> Cls:
    ...


@overload
def contextclass(context_dict: ContextDict) -> Callable[[Cls], Cls]:
    ...


def contextclass(arg):
    if arg is ... or isinstance(arg, ContextVar):
        def wrapper(cls: Cls) -> Cls:
            annotations = getattr(cls, "__annotations__", {})
            meta_bases = tuple(type(base) for base in cls.__bases__
                               # iscontextclass makes loose Mypy type checking
                               if isinstance(base, MetaContextClass))
            if meta_bases:
                context = meta_bases[0].__context__
                assert all(base.__context__ is context
                           for base in meta_bases), \
                    "contextclass base contextclasses " \
                    "must have the same context"
                assert arg is None or arg is context, \
                    "contextclass context must be the same " \
                    "than its base contextclasses"
            else:
                meta_bases = (MetaContextClass,)
                context = default_context if arg is ... else arg
            meta_namespace = {
                field: ContextField(field, getattr(cls, field, ...))
                for field in annotations
            }
            meta = type(f"MetaContextClass{cls.__name__}", meta_bases,
                        meta_namespace)
            assert issubclass(meta, MetaContextClass)
            meta.__context__ = context
            namespace = {
                key: value for key, value in cls.__dict__.items()
                if key not in annotations
            }
            return cast(Cls, meta(cls.__name__, cls.__bases__, namespace))

        return wrapper
    if isclass(arg):
        return contextclass(...)(arg)
    raise NotImplementedError()


class ResetContext(ContextManager):
    def __init__(self, token: Token):
        self.token = token

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.token.var.reset(self.token)


def set_context(context: ContextDict, value: Mapping[str, Any] = None,
                **kwargs) -> ResetContext:
    if value is None and not kwargs:
        token = context.set(context.get({}).copy())
    else:
        token = context.set({**(value or {}), **kwargs})
    return ResetContext(token)


def set_default_context(value: Mapping[str, Any] = None,
                        **kwargs) -> ResetContext:
    return set_context(default_context, value, **kwargs)


def set_contextclass(cls: type, value: Mapping[str, Any] = None,
                     **kwargs) -> ResetContext:
    # iscontextclass makes loose Mypy type checking
    assert isinstance(cls, MetaContextClass)
    # noinspection PyUnresolvedReferences
    return set_context(cls.__context__, value, **kwargs)
