import sys
from qdlgproxy import QDlg, ListBox, observable
from PyQt5.Qt import QApplication, QAbstractItemView


class TestClass:
    def __init__(self):
        self.selectedList = [
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
        ]


@QDlg("ListBox test")
def qDlgClass(dlg):
    t = observable(TestClass())
    s = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
    ]
    ListBox(s, renderer=lambda item: "item %d" % item).multiselect(
        QAbstractItemView.MultiSelection
    ).model(t, attr="selectedList").onSelect(print)
    ListBox(t.selectedList, renderer=lambda item: "item %d" % item).sorted()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qDlgClass.run()
