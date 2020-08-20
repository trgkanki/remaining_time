from PyQt5.Qt import QLayout, QWidget


def addLayoutOrWidget(layout, child):
    if isinstance(child, QLayout):
        layout.addLayout(child)
    elif isinstance(child, QWidget):
        layout.addWidget(child)
    else:
        raise NotImplementedError
