import sys
from qdlgproxy import QDlg, Text, LineEdit  # type: ignore
from PyQt5.Qt import QApplication


@QDlg("LineEdit test dialog", size=[640, 480])
def qDlgClass(dlg):
    Text("Hello world!")
    LineEdit().onInput(lambda s: print("onInput", s)).onChange(
        lambda s: print("onChange", s)
    )


app = QApplication(sys.argv)
qDlgClass.run()
