from contextvars import ContextVar

from pytest import fixture, raises

from contextclasses import (ContextDict, contextclass, default_context,
                            iscontextclass, set_context, set_contextclass,
                            set_default_context)


@fixture(autouse=True)
def init_context():
    with set_default_context():
        yield


def test_set_context():
    assert default_context.get() == {}
    with set_context(default_context, {"a": 0}, b=0):
        assert default_context.get() == {"a": 0, "b": 0}
    assert default_context.get() == {}

    set_context(default_context, {"a": 0})
    assert default_context.get() == {"a": 0}
    with set_context(default_context):
        assert default_context.get() == {"a": 0}
        del default_context.get()["a"]
    assert default_context.get() == {"a": 0}


def test_context_access():
    @contextclass
    class Ctx:
        attr: int

    assert default_context.get() == {}
    with raises(KeyError):
        _ = Ctx.attr
    Ctx.attr = 0
    assert default_context.get() == {"attr": 0}
    assert Ctx.attr == 0
    del Ctx.attr
    assert default_context.get() == {}


def test_context_default():
    @contextclass
    class Ctx:
        attr: int = 0

    assert default_context.get() == {}
    assert Ctx.attr == 0
    assert default_context.get() == {"attr": 0}
    del Ctx.attr
    assert default_context.get() == {}
    assert Ctx.attr == 0
    assert default_context.get() == {"attr": 0}


def test_no_context_without_annotation():
    @contextclass
    class Ctx:
        a: int
        b: int = 0
        c = 0

    Ctx.a = 1
    Ctx.b = 1
    Ctx.c = 1
    assert default_context.get() == {"a": 1, "b": 1}


def test_inheritance():
    @contextclass
    class Ctx:
        a: int

    class ChildCtx(Ctx):
        b: int

    ChildCtx.a = 0
    assert default_context.get() == {"a": 0}
    assert Ctx.a == 0
    assert ChildCtx.a == Ctx.a == 0


custom_context: ContextDict = ContextVar("custom_ctx", default={})


def test_custom_context():
    @contextclass(custom_context)
    class Ctx:
        attr: int

    with raises(KeyError):
        _ = Ctx.attr
    with set_context(custom_context):
        Ctx.attr = 0
        assert Ctx.attr == 0
    with raises(KeyError):
        _ = Ctx.attr


def test_mix_contexts():
    with raises(AssertionError):
        @contextclass(default_context)
        class DefaultCtx:
            pass

        @contextclass(custom_context)
        class CustomCtx(DefaultCtx):
            pass


def test_iscontextclass():
    @contextclass
    class Ctx:
        pass

    assert iscontextclass(Ctx)
    assert not iscontextclass(str)


def test_init_contextclass():
    @contextclass(custom_context)
    class CustomCtx:
        attr: int

    with set_contextclass(CustomCtx):
        CustomCtx.attr = 0
        assert custom_context.get() == {"attr": 0}
    assert custom_context.get() == {}
