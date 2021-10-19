from fx.core.value import Function, FunctionArg
from fx.utils import function


def test_function_result():
    @function()
    def fn(): pass

    assert isinstance(fn, Function)


def test_function_name():
    @function(name="concat")
    def fn(): pass

    assert fn.name == 'concat'


def test_function_name_inference():
    @function()
    def sum(): pass

    assert sum.name == 'sum'


def test_function_signature():
    @function(signature=[FunctionArg('a'), FunctionArg('b')])
    def fn(a, b): pass

    assert fn.signature == [FunctionArg('a'), FunctionArg('b')]


def test_function_signature_inference():
    @function()
    def fn(a, b): pass

    assert fn.signature == [FunctionArg('a'), FunctionArg('b')]
