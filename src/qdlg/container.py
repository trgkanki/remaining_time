from . import stack
from contextlib import ContextDecorator


class QDlgContainer(ContextDecorator):
    """ Base class for widget containing other childs """

    def __enter__(self):
        stack.pushQDlgStack(self)
        return self

    def __exit__(self, *exc):
        stack.popQDlgStack(self)
        return False

    def addChild(self, child):
        return NotImplemented
