import sys
from qdlgproxy import (  # type: ignore
    QDlg,
    ListBox,
)
from PyQt5.Qt import QApplication


class TestClass:
    def __init__(self):
        self.checked1 = False


@QDlg("ListBox test")
def qDlgClass():
    s = [1, 2, 3]
    l = ListBox(s, renderer=lambda item: "item %d" % item).onSelect(print)
    l.select(3)


app = QApplication(sys.argv)
qDlgClass.run()
