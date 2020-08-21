from PyQt5.Qt import QDialog, QVBoxLayout, Qt

from .stack import pushQDlgStack, popQDlgStack, qDlgStackGetDialog
from .utils import addLayoutOrWidget


def QDlg(title, size=None):
    class _QDlg:
        def __init__(self, constructor):
            self.constructor = constructor

        def run(self, *args, **kwargs):
            """Create & show dialog

            Args:
                onClose(accepted): Function to run on close. Defaults to None.
            """
            dlg = QDialog()
            dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            dlg.setWindowTitle(title)

            layout = QVBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)
            self.layout = layout
            dlg.setLayout(layout)

            pushQDlgStack(self)
            self.constructor(dlg, *args, **kwargs)
            popQDlgStack(self)

            dlg.setWindowModality(Qt.WindowModal)
            if size:
                dlg.resize(size[0], size[1])
            dlg.show()
            return dlg.exec_() == QDialog.Accepted

        def addChild(self, child):
            addLayoutOrWidget(self.layout, child)

    return _QDlg
