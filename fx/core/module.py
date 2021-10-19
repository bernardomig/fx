from functools import wraps
from .value import Function


class Module:
    def __dict__(self):
        if hasattr(self, '__functions__'):
            return getattr(self, '__functions__')
        return {}

    def __getitem__(self, key):
        return self.get(key)

    @classmethod
    def get(cls, name):
        if not hasattr(cls, '__functions__'):
            raise KeyError()
        return getattr(cls, '__functions__')[name]

    @classmethod
    def register(cls, name):
        if not hasattr(cls, '__functions__'):
            setattr(cls, '__functions__', {})

        def inner(method):
            cls.__functions__[name] = method
            return method
        return inner


def function(name=None):
    def inner(fn):
        return Function(
            name=name or fn.__name__,
            signature=[],
            fn=fn)
    return inner
