import sys
from qdlgproxy import (  # type: ignore
    QDlg,
    Text,
    LineEdit,
    Button,
    CheckBox,
    HStack,
    Table,
    Tr,
    Td,
)
from PyQt5.Qt import QApplication


class TestClass:
    def __init__(self):
        self.checked1 = False


@QDlg("Table test")
def qDlgClass(dlg):
    with Table():
        with Tr():
            with Td():
                Text("Username")
            with Td():
                username = LineEdit()

        with Tr():
            with Td():
                Text("Password")
            with Td():
                password = LineEdit().passwordInput()

        with Tr():
            with Td(colspan=2):
                with HStack():
                    Text("Remember me?")
                    CheckBox()

        with Tr():
            with Td(colspan=2):
                (
                    Button("Login")
                    .onClick(lambda: print(username.text(), password.text()))
                    .setDefault()
                )


app = QApplication(sys.argv)
qDlgClass.run()
