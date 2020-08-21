from ..stack import qDlgStackTop
from ..utils import addLayoutOrWidget
from ..container import QDlgContainer

from PyQt5.Qt import QGroupBox, QVBoxLayout


class Group(QDlgContainer):
    def __init__(self, title: str):
        self.groupBox = QGroupBox(title)
        self.layout = QVBoxLayout()
        self.groupBox.setLayout(self.layout)
        qDlgStackTop().addChild(self.groupBox)

    def addChild(self, child):
        addLayoutOrWidget(self.layout, child)
        return self
