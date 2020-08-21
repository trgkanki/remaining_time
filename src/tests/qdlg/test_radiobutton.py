import sys
from qdlgproxy import (  # type: ignore
    QDlg,
    RadioButton,
)
from PyQt5.Qt import QApplication


@QDlg("Table test")
def qDlgClass(dlg):
    def onSelect(v):
        print("%s selected" % v)

    RadioButton("Male", value=0).onSelect(onSelect)
    RadioButton("Female", value=1).onSelect(onSelect)


app = QApplication(sys.argv)
qDlgClass.run()
