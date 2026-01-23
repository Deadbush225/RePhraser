from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

import os
import math

from rephraser.lib.RibbonWidget import RibbonWidget
from rephraser.lib.ScrollBar import ScrollBar
from rephraser.lib.TextEdit import TextEdit
from rephraser.lib.helper import *
from rephraser.lib.DarkPallete import enable_dark_titlebar
from rephraser.lib.Logger import Logger
from rephraser import basedir, get_version
import rephraser.images.images  # Resource file for the icons
from pathlib import Path

floor = math.floor

HTML_EXTENSIONS = [".htm", ".html"]


class MainWindow(QMainWindow):
    changed = False

    def __init__(self):
        super().__init__()

        enable_dark_titlebar(self)

        settings = QSettings("Deadbush225", "Rephrase")

        self.setMinimumSize(700, 400)
        self.setWindowIcon(QIcon(os.path.join(basedir, "RePhraser.png")))

        self.path = None
        self.folder = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)

        # Create text editor first (ribbon needs reference to it)
        self.editor = TextEdit(parent=self)
        self.editor.setVerticalScrollBar(ScrollBar(Qt.Vertical))
        self.editor.setTabStopDistance(40)
        self.editor.textChanged.connect(lambda: setattr(self, "changed", True))

        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create and add ribbon widget (after editor is created)
        self.ribbon = RibbonWidget(self)
        main_layout.addWidget(self.ribbon)

        # Add editor to layout
        main_layout.addWidget(self.editor)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Create menu bar (minimal - most functionality is in ribbon)
        self.create_menu_bar()

        # Initialize default font size
        self.editor.setFontPointSize(12)

        # Initialize
        self.update_title()
        self.setMinimumSize(QSize(780, 510))
        self.show()

    def create_menu_bar(self):
        """Create a minimal menu bar with essential items"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        reset_view_action = QAction("Reset View", self)
        reset_view_action.setStatusTip("Reset View")
        reset_view_action.triggered.connect(self.reset_view)
        view_menu.addAction(reset_view_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def reset_view(self):
        """Reset the interface to default state"""
        # Reset ribbon to first tab
        self.ribbon.tab_widget.setCurrentIndex(0)
        
        # Reset author selection to "None"
        if hasattr(self, 'author_combo'):
            self.author_combo.setCurrentIndex(0)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About RePhraser", 
                         f"RePhraser - A rich text editor with author attribution\n\nVersion {get_version()}")

    def refresh_stylesheet(self):
        qApp.setStyleSheet("".join(open(os.path.join(basedir, "dark.qss")).readlines()))

    def open_directory(self):
        self.layout.setCurrentWidget(self.editor)

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self, path=""):
        if self.changed:
            res = self.promptUnsavedChanges()
            print(res)
            if res != "Saved" and res != "Discard":
                return

        print(path)
        # print(type(path))
        if not path:
            print("FIND THE FILE")

            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open file",
                self.folder,
                "HTML documents (*.html)",
            )
            if not path:
                return

        print(path)
        # print(type(path))

        try:
            with open(path, "r") as f:
                text = f.read()
                f.close()
                self.folder = os.path.dirname(path)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            # Qt will automatically try and guess the format as txt/html

            self.editor.setHtml(text)
            self.changed = False
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
                self.update_path(self.path)
                return 1

        except Exception as e:
            self.dialog_critical(str(e))

    def file_saveas(self):
        path, filter_ = QFileDialog.getSaveFileName(
            self,
            "Save file",
            self.folder,
            "HTML documents (*.html)",
        )

        if not path:
            # If dialog is cancelled, will return ''
            return 0
        if Path(path).suffix == "":
            path += ".html"

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
                self.update_path(path)
                return 1

        except Exception as e:
            self.dialog_critical(str(e))

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

    def promptUnsavedChanges(self):
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
            if self.file_save():
                return "Saved"

        elif res == QMessageBox.Discard:
            return "Discard"

        # elif res == QMessageBox.Cancel:
        return "Cancel"

    def closeEvent(self, e):
        if not self.changed or self.editor.toPlainText() == "":
            return

        res = self.promptUnsavedChanges()

        if res == "Saved" or res == "Discard":
            return
        elif res == "Cancel":
            e.ignore()
