from pytest import fixture, raises

from contextclass import Context, context, init_context


def test_init_context():
    assert context.get() == {}
    with init_context(a=0):
        assert context.get() == {"a": 0}
        init_context({"b": 0})
        assert context.get() == {"b": 0}
    assert context.get() == {}


@fixture(autouse=True)
def _init_context(request):
    """Because 'context' is global, tests must be isolated"""
    # init_context test mustn't use the fixture
    if request.node.name == "test_init_context":
        yield
        return
    with init_context():
        yield


def test_context_access():
    class Ctx(Context):
        attr: int

    assert context.get() == {}
    with raises(KeyError):
        _ = Ctx.attr
    Ctx.attr = 0
    assert context.get() == {"attr": 0}
    assert Ctx.attr == 0


def test_context_default():
    class Ctx(Context):
        attr: int = 0

    assert context.get() == {}
    assert Ctx.attr == 0
    assert context.get() == {"attr": 0}


def test_no_context_without_annotation():
    class Ctx(Context):
        a: int
        b: int = 0
        c = 0

    Ctx.a = 1
    Ctx.b = 1
    Ctx.c = 1
    assert context.get() == {"a": 1, "b": 1}


def test_inheritance():
    class Ctx(Context):
        a: int

    class ChildCtx(Ctx):
        b: int

    ChildCtx.a = 0
    assert context.get() == {"a": 0}
    assert Ctx.a == 0
    assert ChildCtx.a == Ctx.a == 0
    with raises(AttributeError):
        assert Context.a == 0  # noqa
