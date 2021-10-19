from dataclasses import dataclass
from fx.core import Integer, Float, Boolean, String, Array, Record
from fx.utils import wrap, unwrap


def test_wrap():
    assert wrap(1) == Integer(1)
    assert wrap(1.) == Float(1.)
    assert wrap(True) == Boolean(True)
    assert wrap(False) == Boolean(False)
    assert wrap('hello') == String('hello')

    assert wrap([]) == Array([])
    assert wrap(['a', 1]) == Array([String('a'), Integer(1)])

    assert wrap({}) == Record({})
    assert wrap({'a': 1}) == Record({'a': Integer(1)})


def test_wrap_objects():
    @dataclass
    class SomeObject:
        a: bool
        b: float

    o = SomeObject(a=True, b=20.)

    assert wrap(o) == Record({'a': Boolean(True), 'b': Float(20.)})
