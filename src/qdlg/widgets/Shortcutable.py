from PyQt5.Qt import QKeySequence


class Shortcutable:
    def shortcut(self, keySequence: str):
        kSeq = QKeySequence(keySequence)
        self.widget.setShortcut(kSeq)
        self.widget.setToolTip(kSeq.toString())

    def default(self):
        self.widget.setDefault(True)
