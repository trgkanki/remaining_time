from ..stack import qDlgStackTop
from ..container import QDlgContainer
from ..utils import addLayoutOrWidget

from PyQt5.Qt import QGridLayout, QVBoxLayout


class Td(QDlgContainer):
    def __init__(self, colspan=1):
        self.colspan = colspan
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        qDlgStackTop().addChild(self)

    def addChild(self, child):
        addLayoutOrWidget(self.layout, child)


class Tr(QDlgContainer):
    def __init__(self):
        self.cols = []
        qDlgStackTop().addChild(self)

    def addChild(self, child):
        assert isinstance(child, Td)
        self.cols.append(child)

    def totalColspan(self):
        return sum(child.colspan for child in self.cols)


class Table(QDlgContainer):
    def __init__(self):
        self.rows = []

    def addChild(self, child):
        assert isinstance(child, Tr)
        self.rows.append(child)

    def __exit__(self, *exc):
        ret = super().__exit__(*exc)

        # build table here
        layout = QGridLayout()
        for y, row in enumerate(self.rows):
            x = 0
            for col in row.cols:
                layout.addLayout(col.layout, y, x, 1, col.colspan)
                x += col.colspan

        qDlgStackTop().addChild(layout)
        return ret
