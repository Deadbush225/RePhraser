from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

import os
import sys
import uuid
import math
import re
import traceback

from rephraser.lib.AuthorTable import AuthorTable
from rephraser.lib.ScrollBar import ScrollBar
from rephraser.lib.TextEdit import TextEdit, PasteFromAuthorDialog
from rephraser.lib.helper import *
from rephraser.lib.Toolbar import Toolbar
from rephraser.lib.DarkPallete import DarkPalette
from rephraser.lib.Logger import Logger

from rephraser import basedir
import rephraser.images.images # Resource file for the icons
from rephraser.lib.DarkPallete import enable_dark_titlebar

floor = math.floor

IMAGE_EXTENSIONS = [".jpg", ".png", ".bmp"]
HTML_EXTENSIONS = [".htm", ".html"]

class MainWindow(QMainWindow):
    changed = False
    dockwidget = None

    def createDock(self):
        dock_widgets = self.findChildren(QDockWidget)
        if self.dockwidget in dock_widgets:
            return

        self.dockwidget = QDockWidget("Change Author")
        self.dockwidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dockwidget.setMaximumWidth(300)
        self.dockwidget.setMinimumWidth(165)

        enable_dark_titlebar(self.dockwidget)

        dock_innerContainer = QWidget()
        self.dockwidget.setWidget(dock_innerContainer)
        dock_layout = QVBoxLayout(dock_innerContainer)

        self.author_table = AuthorTable(parent=self)
        dock_layout.addWidget(self.author_table)

        addAuthor_btn = QPushButton("Add Author")
        addAuthor_btn.clicked.connect(lambda: self.author_table.addAuthor())

        resetFmt_btn = QPushButton("Reset Format")
        resetFmt_btn.clicked.connect(lambda: self.editor.removeCharFormatSelection())

        dock_layout.addWidget(addAuthor_btn)
        dock_layout.addWidget(resetFmt_btn)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)

        # ━━━━━━━━━━━━━━━━━━━ Refresh Stylesheet ━━━━━━━━━━━━━━━━━━ #
        self.refresh_btn = QPushButton("Refresh stylesheet")
        self.refresh_btn.clicked.connect(self.refresh_stylesheet)
        dock_layout.addWidget(self.refresh_btn)
        
        self.dockwidget.closeEvent = lambda event: self.on_dock_close(event)
    
    def on_dock_close(self, event):
        self.removeDockWidget(self.dockwidget)
        self.dockwidget.deleteLater()
        self.dockwidget = None
        event.accept()

    def __init__(self):
        super().__init__()

        enable_dark_titlebar(self)
        
        self.setMinimumSize(700, 400)

        self.setWindowIcon(QIcon(os.path.join(basedir, "RePhraser.png")))

        self.path = None

        self.layout = QVBoxLayout()

        self.editor = TextEdit(parent=self)
        self.editor.setVerticalScrollBar(ScrollBar(Qt.Vertical))
        self.editor.setTabStopDistance(40)
        self.editor.textChanged.connect(lambda: setattr(self, 'changed', True))

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

        # ━━━━━━━━━━━━━━━━━━━━━━━━ Toolbar ━━━━━━━━━━━━━━━━━━━━━━━━ #
        file_toolbar = Toolbar("File", parent=self)

        # ━━━━━━━━━━━━━━━━━━━━━━ Dock Widget ━━━━━━━━━━━━━━━━━━━━━━ #
        self.createDock()

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

        

        # Initialize.
        self.update_format()
        self.update_title()
        self.setMinimumSize(QSize(780, 510))
        self.show()

    def refresh_stylesheet(self):
        qApp.setStyleSheet("".join(open(os.path.join(basedir, "dark.qss")).readlines()))

    def block_signals(self, objects, b):
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
                f.close()
                self.changed = False
                return 1

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
            return 0

        text = (
            self.editor.toHtml()
            if splitext(path) in HTML_EXTENSIONS
            else self.editor.toPlainText()
        )

        try:
            with open(path, "w") as f:
                f.write(text)
                f.close()
                self.changed = False
                return 1

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
        if not self.changed or self.editor.toPlainText() == "":
            return
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Unsaved Changes")
        msg_box.setText("You have unsaved changes. Do you want to save them?")
        save_btn = msg_box.addButton("Save", QMessageBox.AcceptRole)
        discard_btn = msg_box.addButton("Discard", QMessageBox.DestructiveRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)
        msg_box.setDefaultButton(save_btn)
        enable_dark_titlebar(msg_box)
        msg_box.exec_()
        clicked_button = msg_box.clickedButton()
        if clicked_button == save_btn:
            res = QMessageBox.Save
        elif clicked_button == discard_btn:
            res = QMessageBox.Discard
        else:
            res = QMessageBox.Cancel

        if res == QMessageBox.Save:
            if not self.file_save():
                e.ignore()
                return
        elif res == QMessageBox.Cancel:
            e.ignore()
            return
            
    

