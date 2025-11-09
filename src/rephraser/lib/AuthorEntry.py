from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

# todo: use the Qt namespace colors


class AuthorEntry:
    def __init__(
        self,
        author_name: str = "Default",
        foreground: str = "#ffffff",
        background: str = "#a6a6a6",
        weight: int = 100,
        italic: bool = True,
        href: str = "www.example.com",
    ):
        self.author_name = author_name
        self.foreground = foreground if type(foreground) == str else "#ffffff"
        self.background = background if type(background) == str else "#a6a6a6"
        self.weight = weight if type(weight) == int else 100
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
        signature = f"""
            color: {self.foreground};
            background: {self.background};
            font-weight: {self.weight * 8};
            font-style: {"italic" if self.italic else ""};
        """
        return signature
