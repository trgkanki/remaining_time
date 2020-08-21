import sys
from qdlgproxy import QDlg, ListBox, observable
from PyQt5.Qt import QApplication


class TestClass:
    def __init__(self):
        self.selectedList = [3]


@QDlg("ListBox test")
def qDlgClass(dlg):
    t = observable(TestClass())
    s = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ListBox(s, renderer=lambda item: "item %d" % item, multiselect=True).model(
        t, attr="selectedList"
    ).onSelect(print)
    ListBox(t.selectedList, renderer=lambda item: "item %d" % item)


app = QApplication(sys.argv)
qDlgClass.run()
