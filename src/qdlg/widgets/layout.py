from ..stack import qDlgStackTop
from ..container import QDlgContainer

from PyQt5.Qt import QVBoxLayout, QHBoxLayout


class LayoutBase(QDlgContainer):
    def __init__(self, LayoutClass, margin=0):
        self.layout = LayoutClass()
        self.layout.setContentsMargins(margin, margin, margin, margin)
        qDlgStackTop().addChild(self.layout)

    def addChild(self, child):
        self.layout.addWidget(child)


class VStack(LayoutBase):
    def __init__(self, margin=0):
        super().__init__(QVBoxLayout, margin)


class HStack(LayoutBase):
    def __init__(self, margin=0):
        super().__init__(QHBoxLayout, margin)
