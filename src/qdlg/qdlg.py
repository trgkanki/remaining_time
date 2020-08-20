from PyQt5.Qt import QDialog, QVBoxLayout, Qt

from .stack import pushQDlgStack, popQDlgStack


class QDlgWithCallback(QDialog):
    def __init__(self, onClose):
        self.onClose = onClose
        super().__init__()

    def accept(self):
        super().accept(self)
        if self.onClose:
            self.onClose(True)

    def reject(self):
        super().reject()
        if self.onClose:
            self.onClose(False)


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
            self.constructor(*args, **kwargs)
            popQDlgStack(self)

            dlg.setWindowModality(Qt.WindowModal)
            if size:
                dlg.resize(size[0], size[1])
            dlg.show()
            dlg.exec_()

        def addChild(self, child):
            self.layout.addWidget(child)

    return _QDlg
