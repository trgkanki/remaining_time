from aqt import mw
from aqt.webview import AnkiWebView
from aqt.qt import (
    QApplication,
    QUrl,
    QDialog,
    QVBoxLayout,
    Qt,
)

from .resource import getResourcePath


class MiniBrowser(QDialog):
    silentlyClose = True

    def __init__(self, parent, rootHtmlPath, size=None):
        super().__init__(parent)
        mw.setupDialogGC(self)

        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        # Populate content
        self.web = AnkiWebView()
        self.web.set_open_links_externally(False)

        # Support window.close
        self.web.page().windowCloseRequested.connect(self.close)
        l = QVBoxLayout()
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(self.web)
        self.setLayout(l)

        if type(size) == tuple:
            w, h = size
            self.resize(w, h)
            self.show()

        elif size is None:
            self.resize(800, 600)
            self.show()

        elif size == "maximized" or size == "maximize":
            self.resize(800, 600)
            self.showMaximized()

        elif size == "minimized" or size == "minimize":
            self.resize(800, 600)
            self.showMinimized()

        else:
            print("MiniBrowser - bad size (%s)" % size)
            self.resize(800, 600)
            self.show()

        # OK
        self.gotoLocalFile(rootHtmlPath)

    def gotoLocalFile(self, rootHtmlPath):
        rootHtmlPath = getResourcePath(rootHtmlPath)

        # Code from AnkiWebView::_setHtml
        app = QApplication.instance()

        # work around webengine stealing focus on setHtml()
        oldFocus = app.focusWidget()
        self.web.page().setUrl(QUrl.fromLocalFile(rootHtmlPath))
        if oldFocus:
            oldFocus.setFocus()

    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)
