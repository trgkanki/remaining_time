import sys
from qdlgproxy import QDlg, Text, Button  # type: ignore
from PyQt5.Qt import QApplication, QMessageBox


@QDlg("Test dialog", size=[640, 480])
def qDlgClass(dlg):
    Text("Hello world!")

    def onClick():
        QMessageBox.warning(
            None, "test msgbox", "content",
        )

    Button("Hello world!").onClick(onClick)


app = QApplication(sys.argv)
qDlgClass.run()
