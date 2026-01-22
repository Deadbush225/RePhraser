from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

import os
import sys

# import math

# import traceback

from ..lib.ClickableLabel import ClickableLabel
from ..lib.AuthorEntry import AuthorEntry
from ..lib.Stores import store


class AddAuthorDialog(QDialog):

    submit = pyqtSignal(AuthorEntry)

    def __init__(self, entry, parent=None):
        super(QDialog, self).__init__(parent=parent)

        print("TST")
        p = entry.getProperties(include_name=True)
        print(p)

        author_name = p["author_name"]
        foreground = p["foreground"]
        background = p["background"]
        italic = p["italic"]
        weight = p["weight"]
        href = p["href"]

        self.original_row = {
            "author_name": author_name,
            "foreground": foreground,
            "background": background,
            "italic": italic,
            "weight": weight,
            "href": href,
        }

        mainlayout = QVBoxLayout()

        author_cont = QHBoxLayout()
        author_cont.addWidget(QLabel("Author Name: "))
        self.author_field = QLineEdit(author_name)
        author_cont.addWidget(self.author_field)

        foreground_cont = QHBoxLayout()
        foreground_cont.addWidget(QLabel("Foreground: "))
        self.colorPrev_foreground = ClickableLabel(QColor(foreground))
        foreground_cont.addWidget(self.colorPrev_foreground)

        background_cont = QHBoxLayout()
        background_cont.addWidget(QLabel("Background: "))
        self.colorPrev_background = ClickableLabel(QColor(background))
        background_cont.addWidget(self.colorPrev_background)

        weight_cont = QHBoxLayout()
        weight_cont.addWidget(QLabel("Weight: "))
        self.weight_spinbox = QSpinBox()
        self.weight_spinbox.setMinimum(0)
        self.weight_spinbox.setMaximum(100)
        self.weight_spinbox.setSingleStep(1000)
        self.weight_spinbox.setValue(weight)
        weight_cont.addWidget(self.weight_spinbox)

        formatting_cont = QHBoxLayout()
        self.isItalic = QCheckBox("Italic")
        self.isItalic.setChecked(italic)
        # self.isBold = QCheckBox("Bold")
        # formatting_cont.addWidget(self.isBold)
        formatting_cont.addWidget(self.isItalic)

        href_cont = QHBoxLayout()
        href_cont.addWidget(QLabel("Href: "))
        self.href_field = QLineEdit()
        self.href_field.setText(href)
        href_cont.addWidget(self.href_field)

        self.saveAuthor_btn = QPushButton("Save Author")

        # close before adding lambda function
        self.saveAuthor_btn.clicked.connect(lambda: self.fin())

        mainlayout.addLayout(author_cont)
        mainlayout.addLayout(foreground_cont)
        mainlayout.addLayout(background_cont)
        mainlayout.addLayout(weight_cont)
        mainlayout.addLayout(formatting_cont)
        mainlayout.addLayout(href_cont)
        mainlayout.addWidget(self.saveAuthor_btn)

        self.setLayout(mainlayout)

    def fin(self):
        author_name = self.author_field.text()
        color = self.colorPrev_foreground.color.name(QColor.HexArgb)
        background = self.colorPrev_background.color.name(QColor.HexArgb)
        weight = self.weight_spinbox.value()
        italic = self.isItalic.isChecked()
        href = self.href_field.text()
        # rowNum = self.selectedRows()[0] if overrideRow else None

        # print(self.parent().author_dictionary)
        if self.original_row["author_name"] == author_name:
            # means the override was meant
            print("OVERRIDE MODE")
            pass

        self.done(QDialog.Accepted)

        self.submit.emit(
            AuthorEntry(author_name, color, background, weight, italic, href)
        )


class AuthorTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent_ = parent

        self.settings = QSettings("DeadBush225", "RePhraser")

        # store.author_dictionary = {}
        store.author_dictionary = self.settings.value("authors")
        # print(retrieved)

        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(["Author Signature"])
        self.verticalHeader().hide()
        # store.author_dictionary = author_dictionary

        if not store.author_dictionary:
            store.author_dictionary = {
                "Ai": {
                    "italic": False,
                    "weight": 0,
                    "foreground": QColor("#fc3737"),
                    "background": QColor("#fc6f37"),
                    "href": "WWW",
                },
                "ChatGPT": {
                    "italic": False,
                    "weight": 100,
                    "foreground": QColor("#3772fc"),
                    "background": QColor("#53D85A"),
                    "href": "AAA",
                },
                "Rhixie": {
                    "italic": True,
                    "weight": 0,
                    "foreground": QColor("#fcdb37"),
                    "background": QColor("#9037fc"),
                    "href": "CCC",
                },
            }

        keys = store.author_dictionary.keys()
        for author_name in keys:
            if not author_name in store.author_dictionary:
                print(f"is '{author_name}' in {store.author_dictionary}?")
                continue

            # print("AUTHOR NAME")
            # print(store.author_dictionary[author_name])

            self.addEntry(
                AuthorEntry(author_name, **store.author_dictionary[author_name])
            )

        # self.author_table.resizeColumnsToContents()
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.cellDoubleClicked.connect(
            lambda row, col: self.addAuthor(
                author_name=self.cellWidget(row, 0).text(), row_count=row
            )
        )

        self.cellClicked.connect(self.table_selection_changed)

    def addAuthor(self, author_name="", row_count=None):
        print(f"ADDING AUTHOR: {author_name}")

        new_entry = AuthorEntry(author_name=author_name)

        if row_count and author_name:  # `author_name` is just for error handling
            new_entry.foreground = QColor(
                store.author_dictionary[author_name]["foreground"],
            )
            new_entry.background = QColor(
                store.author_dictionary[author_name]["background"],
            )
            new_entry.italic = store.author_dictionary[author_name]["italic"]
            new_entry.weight = store.author_dictionary[author_name]["weight"]
            new_entry.href = store.author_dictionary[author_name]["href"]

        self.addAuthorWidget = AddAuthorDialog(new_entry, parent=self)
        self.addAuthorWidget.submit.connect(
            lambda entry: self.addEntry(entry, row_count=row_count),
        )

        self.addAuthorWidget.exec_()

    def addEntry(self, entry, row_count=None):
        if row_count == None:
            row_count = self.rowCount()
            self.insertRow(row_count)

            store.author_dictionary[entry.author_name] = entry.getProperties()

        elif row_count != None:
            print("ROW DEFINED: OVERRIDING")

            # row is defined which means it is overriden
            # replace old name with new
            old_name = self.cellWidget(self.selectedRows()[0], 0).text()
            # store.author_dictionary = {
            #     (key if key != old_name else author_name): value
            #     for (key, value) in store.author_dictionary.items()
            # }
            store.author_dictionary[old_name] = entry.getProperties()

        self.saveSettings()
        # print(self.settings.value("authors"))

        textCell = QTableWidgetItem(entry.author_name)
        textCell.setFlags(Qt.ItemIsSelectable)

        # self.setItem(row_count, 0, textCell)

        signature_preview = QLabel(entry.author_name)
        signature_preview.setAlignment(Qt.AlignCenter)
        signature_preview.setStyleSheet(entry.getStyleSheet())

        self.setCellWidget(row_count, 0, signature_preview)

    def table_selection_changed(self, row, col):
        print(f"SELECTION CHANGED {row}")
        # selected_rows = {r.row() for r in self.selectedIndexes()}

        # if len(selected_rows) != 1:
        #     return

        # print("CHANGING AUTHOR")
        # selected_row = list(selected_rows)[0]
        selected_row = row

        author_name = self.cellWidget(selected_row, 0).text()

        self.parent_.editor.setTextCharFormat(author_name)
        self.parent_.editor.setCharFormatSelection()
        self.parent_.editor.setFocus()

    def mousePressEvent(self, e):
        super().mousePressEvent(e)

        if e.button() != Qt.RightButton:
            return

        print("MOUSE RIGHT CLICK")

        selected_rows = self.selectedRows()
        # selected_rows.sort()

        if len(selected_rows) == 1:
            selected_row = selected_rows[0]
            print("TRYING TO DELETE")
            name = self.item(selected_row, 0).text()
            print(name)
            print(store.author_dictionary)

            store.author_dictionary.pop(name)
            self.removeRow(selected_row)

            self.saveSettings()

    def saveSettings(self):
        self.settings.setValue("authors", store.author_dictionary)

    def selectedRows(self):
        return list(set([r.row() for r in self.selectedIndexes()]))
