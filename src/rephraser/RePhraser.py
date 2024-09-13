from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

import os
import sys
import uuid
import math

import re

# from zipfile import ZipFile

import traceback

from rephraser.lib.AuthorTable import AuthorTable
from rephraser.lib.ScrollBar import ScrollBar
from rephraser.lib.TextEdit import TextEdit, PasteFromAuthorDialog
from rephraser.lib.helper import *
from rephraser.lib.Toolbar import Toolbar
from rephraser.lib.DarkPallete import DarkPalette

from rephraser import basedir

import rephraser.images.images

floor = math.floor

IMAGE_EXTENSIONS = [".jpg", ".png", ".bmp"]
HTML_EXTENSIONS = [".htm", ".html"]

# old_basedir = os.path.dirname(__file__)
# print(old_basedir)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(os.path.join(basedir, "RePhraser.png")))

        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None

        # self.layout = QStackedLayout()
        self.layout = QVBoxLayout()

        # mandatoryFileOpenContainer = QWidget()

        # fileOpen_layout = QVBoxLayout()
        # fileOpen_layout.setAlignment(Qt.AlignCenter)

        # fileOpen_label = QLabel("Hey, Open a Project Folder first")
        # fileOpen_btn = QPushButton("Open Dir")
        # fileOpen_btn.clicked.connect(self.open_directory)

        # fileOpen_layout.addWidget(fileOpen_label)
        # fileOpen_layout.addWidget(fileOpen_btn)

        # mandatoryFileOpenContainer.setLayout(fileOpen_layout)
        # self.layout.addWidget(mandatoryFileOpenContainer)

        self.editor = TextEdit(parent=self)
        self.editor.setVerticalScrollBar(ScrollBar(Qt.Vertical))
        self.editor.setTabStopDistance(40)

        # Setup the QTextEdit editor configuration
        # self.editor.setAutoFormatting(QTextEdit.AutoAll)

        self.layout.addWidget(self.editor)
        # layout.setSpacing(0)
        # layout.setContentsMargins(5, 5, 5, 5)

        container = QWidget()
        container.setLayout(self.layout)

        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Uncomment to disable native menubar on Mac
        # self.menuBar().setNativeMenuBar(False)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Toolbar ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
        file_toolbar = Toolbar("File", parent=self)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━ Dock Widget ━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
        dockwidget = QDockWidget("Change Author")
        dockwidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dockwidget.setMaximumWidth(176)
        dockwidget.setMinimumWidth(165)

        dock_innerContainer = QWidget()
        dockwidget.setWidget(dock_innerContainer)
        dock_layout = QVBoxLayout(dock_innerContainer)

        self.author_table = AuthorTable(parent=self)
        dock_layout.addWidget(self.author_table)

        addAuthor_btn = QPushButton("Add Author")
        addAuthor_btn.clicked.connect(lambda: self.author_table.addAuthor())

        resetFmt_btn = QPushButton("Reset Format")
        resetFmt_btn.clicked.connect(lambda: self.editor.removeCharFormatSelection())

        dock_layout.addWidget(addAuthor_btn)
        dock_layout.addWidget(resetFmt_btn)

        self.addDockWidget(Qt.RightDockWidgetArea, dockwidget)

        # Initialize default font size.
        # self.editor.setFont(font)
        # We need to repeat the size to init the current format.
        self.editor.setFontPointSize(12)

        # ━━━━━━━━━━━━━━━━━━━━━━━ Initialize Contents ━━━━━━━━━━━━━━━━━━━━━━━ #
        # self.file_open(
        #     os.path.join(os.path.dirname(os.path.dirname(__file__)), "test.html")
        # )

        # signals
        self.editor.selectionChanged.connect(self.update_format)

        # ━━━━━━━━━━━━━━━━━━━━━━━━ Refresh Stylesheet ━━━━━━━━━━━━━━━━━━━━━━━ #
        self.refresh_btn = QPushButton("Refresh stylesheet")
        self.refresh_btn.clicked.connect(self.refresh_stylesheet)
        dock_layout.addWidget(self.refresh_btn)

        # Initialize.
        self.update_format()
        self.update_title()
        self.setMinimumSize(QSize(780, 510))
        self.show()

    def refresh_stylesheet(self):
        qApp.setStyleSheet("".join(open(os.path.join(basedir, "dark.qss")).readlines()))

    def block_signals(self, objects, b):
        # print(objects)
        for o in objects:
            o.blockSignals(b)

    def update_format(self):
        """
        Update the font format toolbar/actions when a new text selection is made. This is neccessary to keep
        toolbars/etc. in sync with the current edit state.

        > the current format in the toolbar doesn't represent the format of the selected text, but the format present in the cursor
        """

        # self.editor.textIsSelected = True

        # print("selection changed")
        # Disable signals for all format widgets, so changing values here does not trigger further formatting.
        self.block_signals(self._format_actions, True)

        # self.fonts.setCurrentFont(self.editor.currentFont())
        # Nasty, but we get the font-size as a float but want it was an int

        cursor = self.editor.textCursor()
        # cursor.charFormat().fontPointSize()
        charFormat = cursor.charFormat()
        blockFormat = cursor.blockFormat()

        # todo: we don't need to update Font settings since we always override the inserted text with the default TextFormat
        # self.fontsize.setCurrentText(str(int(charFormat.fontPointSize())))

        # self.italic_action.setChecked(charFormat.fontItalic())
        # self.underline_action.setChecked(charFormat.fontUnderline())
        # self.bold_action.setChecked(charFormat.fontWeight() == 100)

        self.alignl_action.setChecked(blockFormat.alignment() == Qt.AlignLeft)
        self.alignc_action.setChecked(blockFormat.alignment() == Qt.AlignCenter)
        self.alignr_action.setChecked(blockFormat.alignment() == Qt.AlignRight)
        self.alignj_action.setChecked(blockFormat.alignment() == Qt.AlignJustify)

        self.block_signals(self._format_actions, False)

    def open_directory(self):
        self.layout.setCurrentWidget(self.editor)

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self, path=""):

        print(path)
        # print(type(path))
        if not path:
            print("FIND THE FILE")
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open file",
                "",
                "HTML documents (*.html)",
            )

        print(path)
        # print(type(path))

        try:
            with open(path, "r") as f:
                text = f.read()

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            # Qt will automatically try and guess the format as txt/html

            self.editor.setHtml(text)
            # self.update_title()
            self.update_path(path)

    def file_save(self):
        if self.path is None:
            # If we do not have a path, we need to use Save As.
            return self.file_saveas()

        text = (
            self.editor.toHtml()
            if splitext(self.path) in HTML_EXTENSIONS
            else self.editor.toPlainText()
        )

        try:
            with open(self.path, "w") as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save file",
            "",
            "HTML documents (*.html)",
        )

        if not path:
            # If dialog is cancelled, will return ''
            return

        text = (
            self.editor.toHtml()
            if splitext(path) in HTML_EXTENSIONS
            else self.editor.toPlainText()
        )

        try:
            with open(path, "w") as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.update_path(path)

    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.editor.print_(dlg.printer())

    def update_path(self, path):
        self.path = path
        splitPath = os.path.split(path)
        self.dir = splitPath[0]
        self.fullName = splitPath[1]
        self.baseName = ".".join(self.fullName.split(".")[0:-1])
        self.update_title()

    def update_title(self):
        self.setWindowTitle(
            "%s - RePhraser" % (self.fullName if self.path else "Untitled")
        )

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0)

    def closeEvent(self, e):
        if self.editor.toPlainText():
            self.file_save()
