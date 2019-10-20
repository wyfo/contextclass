from typing import Any, Iterator, Mapping, MutableMapping

from contextclasses import fields
from contextclasses.contextclass import (Field, MetaContextClass,
                                         check_contextclass)


class ContextMapping(MutableMapping[str, Any]):
    def __init__(self, cls: type):
        assert isinstance(cls, MetaContextClass)
        self.aliased: Mapping[str, Field] = {field.alias: field
                                             for field in fields(cls).values()}

    def __getitem__(self, k: str) -> Any:
        try:
            return self.aliased[k].__get__(..., ...)
        except AttributeError:
            raise KeyError(self.aliased[k])

    def __setitem__(self, k: str, v: Any) -> None:
        return self.aliased[k].__set__(..., v)

    def __delitem__(self, v: str) -> None:
        raise NotImplementedError("deletion is not supported on contextclass "
                                  "mapping")

    def __len__(self) -> int:
        return sum(1 for _ in iter(self))

    def __iter__(self) -> Iterator[str]:
        for alias, field in self.aliased.items():
            if field.isset:
                yield alias


def asmapping(cls: type) -> MutableMapping[str, Any]:
    """
    :param cls: a contextclass
    :return: a mutable mapping wrapping the contextclass
    """
    check_contextclass(cls)
    return ContextMapping(cls)
