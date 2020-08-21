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
    QObservable,
)
from PyQt5.Qt import QApplication


@QObservable
class TestClass:
    def __init__(self):
        self.checked1 = False


@QDlg("Table test")
def qDlgClass():
    obj = TestClass()
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
                    CheckBox().model(obj, "checked1")
                    CheckBox().model(obj, "checked1")
                    CheckBox().model(obj, "checked1")

        with Tr():
            with Td(colspan=2):
                (
                    Button("Login")
                    .onClick(lambda: print(username.text(), password.text()))
                    .setDefault()
                )


app = QApplication(sys.argv)
qDlgClass.run()
