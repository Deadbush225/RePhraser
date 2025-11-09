from PyQt5.QtWidgets import QLabel, QColorDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal


class ClickableLabel(QLabel):

    clicked = pyqtSignal()

    def __init__(self, color: QColor):
        super(QLabel, self).__init__()
        self.setGeometry(100, 100, 200, 60)

        self.color = color
        self.redrawLabel()

        self.clicked.connect(self.changeColor)

    def mousePressEvent(self, e):
        self.clicked.emit()

    def changeColor(self):
        print(f"Changing {self.color.name()}")
        color = QColorDialog.getColor(
            initial=self.color,
            title="Select Color",
            options=QColorDialog.ShowAlphaChannel,
        )
        self.color = color if color.isValid() else self.color
        print(f"to {self.color.name()}")

        # setting option
        # dialog.setOption(QColorDialog.ShowAlphaChannel)

        # executing the dialog
        # dialog.exec_()
        self.redrawLabel()

    def redrawLabel(self):

        self.setStyleSheet(
            "QLabel {"
            f"background-color : {self.color.name()};"
            "border : 1px solid black;"
            "}"
        )
