from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

# todo: use the Qt namespace colors


class AuthorEntry:
    def __init__(
        self,
        author_name="Default",
        foreground=QColor(Qt.white),
        background=QColor(Qt.darkGray),
        weight=100,
        italic=True,
        href="www.example.com",
    ):
        self.author_name = author_name
        self.foreground = foreground
        self.background = background
        self.weight = weight
        self.italic = italic
        self.href = href

    def getProperties(self, include_name=False) -> dict:
        prop = {
            "foreground": self.foreground,
            "background": self.background,
            "italic": self.italic,
            "weight": self.weight,
            "href": self.href,
        }

        if include_name:
            prop["author_name"] = self.author_name

        return prop

    def getStyleSheet(self) -> str:
        return f"""
            color: {self.foreground};
            background: {self.background};
            font-weight: {self.weight * 8};
            font-style: {"italic" if self.italic else ""};
        """
