import sys
from qdlgproxy import (  # type: ignore
    QDlg,
    Button,
)
from PyQt5.Qt import QApplication


@QDlg("OK/reject test")
def qDlgClass(dlg):
    Button("OK").onClick(dlg.accept)
    Button("Cancel").onClick(dlg.reject)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    print(qDlgClass.run())
    print(qDlgClass.run())


def test_wrong():
    ## This test shouldn't be run by nosetests
    assert False
