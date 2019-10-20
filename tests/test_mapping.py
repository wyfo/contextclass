from pytest import raises

from contextclasses import asmapping, contextclass, field


def test_asmapping():
    """Contextclass can be wrapped into a mutable mapping"""
    with raises(ValueError):
        asmapping(str)

    @contextclass
    class Ctx:
        attr: int

    mapping = asmapping(Ctx)
    assert len(mapping) == 0
    assert mapping == {}

    with raises(KeyError):
        _ = mapping["attr"]
    Ctx.attr = 0
    assert mapping["attr"] == 0

    mapping["attr"] = 1
    assert Ctx.attr == 1
    assert mapping == {"attr": 1}

    # Deletion not supported
    with raises(NotImplementedError):
        del mapping["attr"]

    # Like a regular mapping
    with raises(KeyError):
        _ = mapping["not_attr"]

    # To assign a value to multiple value of a contextclass
    asmapping(Ctx).update(attr=2)
    assert Ctx.attr == 2


def test_alias():
    """Contextclass field can be aliased in mapping"""

    @contextclass
    class Ctx:
        aliased: int = field(alias="alias")

    mapping = asmapping(Ctx)
    assert mapping == {}
    with raises(KeyError):
        _ = mapping["alias"]
    mapping["alias"] = 0
    assert mapping == {"alias": 0}
