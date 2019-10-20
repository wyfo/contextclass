from typing import List

from pytest import raises

from contextclasses import contextclass, field, fields, iscontextclass


def test_context_access():
    """Basic example"""

    @contextclass
    class Ctx:
        attr: int

    # Non initialized field access raises LookupError (like ContextVar)
    with raises(AttributeError):
        _ = Ctx.attr
    Ctx.attr = 0
    assert Ctx.attr == 0


def test_context_default():
    """Attribute with default value"""

    @contextclass
    class Ctx:
        attr: int = 0

    # Defaulted attributes can be accessed without initialization (narmol)
    assert Ctx.attr == 0
    Ctx.attr = 1
    assert Ctx.attr == 1


def test_field():
    """Use of contextclass.field"""

    @contextclass
    class Ctx:
        default: int = field(default=0)
        default_factory: List[int] = field(default_factory=list)

    assert Ctx.default == 0
    assert Ctx.default_factory == []

    # cannot specified both default and default factory
    with raises(ValueError):
        field(default=0, default_factory=lambda: 0)


def test_fields():
    """Use of contextclass.fields"""
    with raises(ValueError):
        fields(str)

    @contextclass
    class Ctx:
        attr1: int
        attr2: int = 0
        attr3: int = field(default_factory=lambda: 0)

    assert fields(Ctx).keys() == {"attr1", "attr2", "attr3"}


def test_mutable_default():
    """Mutable values should not be used as default;
       use default_facotry instead"""
    with raises(ValueError):
        @contextclass
        class Ctx:
            attr: List = []
    with raises(ValueError):
        @contextclass
        class Ctx:
            attr: List = field(default=[])


def test_complex_initialization():
    """If needed (advanced use), factory can even use reference to other var"""

    def make_composed():
        return [Ctx.simple]

    @contextclass
    class Ctx:
        simple: str = "ok"
        composed: List[str] = field(default_factory=make_composed)

    assert Ctx.composed == ["ok"]


def test_no_context_without_annotation():
    """Only annotated field will be used in context"""

    @contextclass
    class Ctx:
        a: int
        b: int = 0
        c = 0

    assert fields(Ctx).keys() == {"a", "b"}


def test_inheritance():
    """Contextclasses can be inherited by other (non)contextclasses"""

    @contextclass
    class Ctx:
        a: int

    @contextclass
    class ChildCtx(Ctx):
        pass

    class NotCtx(Ctx):
        pass

    with raises(AttributeError):
        _ = ChildCtx.a
    with raises(AttributeError):
        _ = NotCtx.a
    ChildCtx.a = 0
    assert ChildCtx.a == Ctx.a == NotCtx.a == 0
    assert fields(Ctx).keys() == fields(ChildCtx).keys()


def test_iscontextclass():
    """Do we need a description? :)"""

    @contextclass
    class Ctx:
        pass

    assert iscontextclass(Ctx)
    assert not iscontextclass(str)
