from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import (Any, Callable, Dict, Mapping, Optional, Sequence, Tuple,
                    Type, TypeVar, cast)

ctx_var: ContextVar[Dict[type, Dict[str, Any]]] = \
    ContextVar("contextclass")
ctx_var.set({})

NO_DEFAULT = object()


class MetaContextClass(type):
    __context_fields__: Sequence[str]


@dataclass
class Field:
    _alias: Optional[str] = None
    default: Any = NO_DEFAULT
    default_factory: Optional[Callable[[], Any]] = None
    # set in __set_name__
    name: str = cast(str, ...)
    owner: Type[MetaContextClass] = cast(type, ...)
    key: str = cast(str, ...)

    @property
    def alias(self) -> str:
        return self._alias or self.name

    @property
    def has_default(self) -> bool:
        return (self.default is not NO_DEFAULT or
                self.default_factory is not None)

    @staticmethod
    def from_attribute(field: Any) -> Field:
        if isinstance(field, Field):
            return field
        if field is NO_DEFAULT:
            return Field()
        return Field(default=field)

    def __post_init__(self):
        if isinstance(self.default, (list, dict, set)):
            raise ValueError(f"mutable default {type(self.default)} is not "
                             f"allowed for context field: use default_factory")

    def __set_name__(self, owner: type, name: str):
        # Because field can be used as descriptor in decorated class
        # __set_name__ is only executed for MetaContextClass
        if issubclass(owner, MetaContextClass):
            self.name = name
            self.owner = owner
            self.key = f"{owner.__name__}_{name}"

    @property
    def isset(self) -> bool:
        return self.has_default or self.key in ctx_var.get()[self.owner]

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            ctx = ctx_var.get()[self.owner]
            if self.key in ctx:
                return ctx[self.key]
            elif self.default is not NO_DEFAULT:
                self.__set__(instance, self.default)
                return self.default
            elif self.default_factory is not None:
                default = self.default_factory()
                self.__set__(instance, default)
                return default
            else:
                raise AttributeError(self.name)

    def __set__(self, instance, value):
        ctx_var.set({**ctx_var.get(), self.owner: {
            **ctx_var.get()[self.owner], self.key: value
        }})


def field(*, alias: Optional[str] = None, default: Any = NO_DEFAULT,
          default_factory: Optional[Callable[[], Any]] = None) -> Any:
    """
    :param alias: alias of the field (for serialization etc.)
    :param default: default value
    :param default_factory: default factory for default value
    """
    assert default_factory is None or callable(default_factory), \
        "default_factory must be callable"
    if default is not NO_DEFAULT and default_factory is not None:
        raise ValueError("cannot specify both default and default_factory")
    return Field(alias, default, default_factory)


def iscontextclass(cls: type) -> bool:
    """Returns if a class is a contextclass"""
    return isinstance(cls, MetaContextClass)


def check_contextclass(cls: type):
    if not iscontextclass(cls):
        raise ValueError(f"{cls} is not a contextclass")


def fields(cls: type) -> Mapping[str, Field]:
    check_contextclass(cls)
    assert isinstance(cls, MetaContextClass)
    # noinspection PyUnresolvedReferences
    return {field: getattr(type(cls), field)
            for field in cls.__context_fields__}


Cls = TypeVar("Cls", bound=type)


def contextclass(cls: Cls) -> Cls:
    """
    Returns the same class as was passed in, with class variables mapped
    on a ContextVars.
    """
    # Use cls.__dict__["__annotations__"] instead of cls.__annotations__
    # because inheritance of cls.__annotations__ (cf. test_inheritance)
    annotations = cls.__dict__.get("__annotations__", {})
    if isinstance(cls, MetaContextClass):
        meta_bases: Tuple[type, ...] = (type(cls),)
    else:
        meta_bases = (MetaContextClass, type(cls))
    meta_namespace = {
        field: Field.from_attribute(getattr(cls, field, NO_DEFAULT))
        for field in annotations
    }
    meta = type(f"MetaContextClass{cls.__name__}", meta_bases, meta_namespace)
    assert issubclass(meta, MetaContextClass)
    parent_fields = getattr(meta, "__context_fields__", [])
    meta.__context_fields__ = [*parent_fields, *annotations]
    ctx_var.get()[meta] = {}
    namespace = {
        key: value for key, value in cls.__dict__.items()
        if key not in annotations
    }
    return cast(Cls, meta(cls.__name__, cls.__bases__, namespace))
