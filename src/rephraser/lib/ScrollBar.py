from PyQt5.QtWidgets import QScrollBar


class ScrollBar(QScrollBar):
    def __init__(self, *args, **kwargs):
        super(QScrollBar, self).__init__(*args, **kwargs)

    def enterEvent(self, e):
        self.setStyleSheet(
            """
        QScrollBar::vertical:hover {
            min-height: 0px;
            border: 0px solid red;
            border-radius: 4px;
            /*width: 8px;*/
            width: 4px;
        }"""
        )

    def leaveEvent(self, e):
        self.setStyleSheet("")
