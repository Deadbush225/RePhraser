from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from rephraser.lib.helper import *
from rephraser.lib.Stores import store
from rephraser.lib.qt_helper import HLine
from rephraser.lib.Logger import Logger
from rephraser.lib.DarkPallete import enable_dark_titlebar

import math

IMAGE_EXTENSIONS = [".jpg", ".png", ".bmp"]


class PasteFromAuthorDialog(QDialog):

    author_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent_ = parent
        self.setWindowTitle("Paste as Author")

        mainlayout = QVBoxLayout()

        author_cont = QHBoxLayout()

        self.author_cmbx = QComboBox()
        self.fillComboBox()

        author_cont.addWidget(QLabel("Existing Author: "))
        author_cont.addWidget(self.author_cmbx)

        self.saveAuthor_btn = QPushButton("Ok")
        self.saveAuthor_btn.clicked.connect(lambda: self.fin())

        self.newAuthor_btn = QPushButton("Add as new Author")
        self.newAuthor_btn.clicked.connect(self.addNewAuthor)

        hline = HLine(parent=self)

        mainlayout.addLayout(author_cont)
        mainlayout.addWidget(self.saveAuthor_btn)
        mainlayout.addWidget(hline)
        mainlayout.addWidget(self.newAuthor_btn)

        self.setLayout(mainlayout)

    def addNewAuthor(self):
        self.parent_.parent_.author_table.addAuthor("")
        self.fillComboBox()

    def fillComboBox(self):
        self.author_cmbx.clear()
        self.author_cmbx.addItems(store.author_dictionary.keys())

    def fin(self):
        self.done(QDialog.Accepted)
        self.author_selected.emit(self.author_cmbx.currentText())


class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.parent_ = parent

        self.setMinimumWidth(580)
        
        # Make the caret thicker
        self.setCursorWidth(3)

        self.parent_ = parent
        self.textIsSelected = False
        self.dropped_text = None

        self.textCharFormat = QTextCharFormat()
        self.defaultCharFormat = QTextCharFormat()  # reset format
        font = QFont("Lexend", 12)
        self.defaultCharFormat.setFont(font)

        self.images = {}
        self.DPM = math.floor(1 * 39.37)

        # print(self.editor.verticalScrollBar().styleSheet())
        self.verticalScrollBar().setStyle(
            QCommonStyle()
        )  # to make the transparency work

        # self.setDisabled(True)

    def dropEvent(self, event):
        m = event.mimeData()
        if m.hasText():
            self.dropped_text = m.text()

        super().dropEvent(event)

    def canInsertFromMimeData(self, source):
        if source.hasImage():
            # print("I CAN INSERT IMAGE")
            # print(self.parent().path)
            # if not os.path.exist(self.parent().path):
            #     self.parent().file_save()

            # # todo: emit a signal indicating that we need to save first
            # if os.path.exists(self.parent().path):
            #     return True

            # return False
            return True
        else:
            return super(TextEdit, self).canInsertFromMimeData(source)

    def insertFromMimeData(self, source):
        print("INSERT FROM MIME DATA")
        cursor = self.textCursor()
        document = self.document()

        if source.hasImage():
            print("I CAN INSERT IMAGE")
            print(self.parent_.path)
            if self.parent_.path is None:
                QMessageBox.information(
                    self,
                    "Save Required",
                    "Please save the file before inserting images.",
                )
                self.parent_.file_save()

            # recheck after displaying save dialog
            if (self.parent_.path is None) or (not os.path.exists(self.parent_.path)):
                return
                # return True

            print("INSERTING IMAGE")
            image = source.imageData()

            uuid = self.addImageResource(image)
            # fragment = QTextDocumentFragment.fromHtml(
            #     f"<img src='{source.text()}' height='{height}' width='{width}'></img>"
            # )

            # cursor.insertFragment(fragment)
            self.setAlignment(Qt.AlignCenter)
            cursor.insertImage(uuid)
            # cursor.insertImage(uuid)
            return

        elif source.hasText():
            selectedTextIsBeingDragged = self.dropped_text == source.text()

            if not selectedTextIsBeingDragged:
                te = PasteFromAuthorDialog(parent=self)

                enable_dark_titlebar(te)
                te.author_selected.connect(self.setTextCharFormat)
                if te.exec_() == QDialog.Rejected:
                    self.textCharFormat = self.defaultCharFormat

                self.setCharFormatSelection()
                self.textCursor().insertText(source.text(), self.textCharFormat)
                self.removeCharFormatSelection()
            elif selectedTextIsBeingDragged:
                self.textCursor().insertHtml(source.html())

            return

        elif source.hasUrls():
            for u in source.urls():
                file_ext = splitext(str(u.toLocalFile()))
                if u.isLocalFile() and file_ext in IMAGE_EXTENSIONS:
                    image = QImage(u.toLocalFile())
                    # document.addResource(QTextDocument.ImageResource, u, image)
                    # uuid = hexuuid()
                    print("IMAGE FROM FILE")
                    uuid = self.addImageResource(image)
                    cursor.insertImage(uuid)

                else:
                    # If we hit a non-image or non-local URL break the loop and fall out
                    # to the super call & let Qt handle it
                    break

            else:
                # If all were valid images, finish here.
                return

        super().insertFromMimeData(source)

    def keyPressEvent(self, e):
        if e.text().isalnum() or (e.text() == " "):
            # self.removeCharFormatSelection()
            Logger.w("ALPHANUMERIC", Logger.INFO)
            self.textCharFormat = QTextCharFormat(self.defaultCharFormat)
            self.defaultCharFormat.setFontPointSize(self.fontPointSize())
            self.defaultCharFormat.setFont(self.currentFont())
            self.textCursor().insertText(e.text(), self.defaultCharFormat)
            # self.parent_.update_format()
            return

        super().keyPressEvent(e)

    def setCharFormatSelection(self):
        self.textCursor().setCharFormat(self.textCharFormat)

    def removeCharFormatSelection(self):
        self.textCursor().setCharFormat(self.defaultCharFormat)

    def setTextCharFormat(self, authorName):
        prop = store.author_dictionary[authorName]
        Logger.w(prop, Logger.INFO)

        # Create a new format based on current font to preserve font family and size
        self.textCharFormat = QTextCharFormat()
        self.textCharFormat.setFont(self.currentFont())
        self.textCharFormat.setFontPointSize(self.fontPointSize())
        
        # Apply italic formatting
        self.textCharFormat.setFontItalic(prop["italic"])
        
        # Convert weight to Qt font weight system
        # Qt uses: Light=25, Normal=50, DemiBold=63, Bold=75, Black=87
        # Convert from 0-100 scale to Qt scale
        weight_value = prop["weight"]
        if weight_value >= 90:
            qt_weight = QFont.Black  # 87
        elif weight_value >= 70:
            qt_weight = QFont.Bold  # 75
        elif weight_value >= 55:
            qt_weight = QFont.DemiBold  # 63
        elif weight_value >= 35:
            qt_weight = QFont.Normal  # 50
        else:
            qt_weight = QFont.Light  # 25
        
        self.textCharFormat.setFontWeight(qt_weight)
        
        # Apply colors
        self.textCharFormat.setForeground(QColor(prop["foreground"]))
        self.textCharFormat.setBackground(QColor(prop["background"]))

    def resizeEvent(self, e):
        # print(f"{self.document().idealWidth()} : {self.width()}")

        # cur_pos = 0

        # while cur_pos < self.textCursor().position():
        #     found_cursor = self.document().find(self.image_regex, cur_pos)

        #     if found_cursor.position() == -1:
        #         print("NO IMAGE FOUND")
        #         break

        #     text = found_cursor.selectedText()

        #     self.image_regex.indexIn(text)
        #     print(f"ima: {self.image_regex.cap(1)}")
        #     print(f"cur_pos: {cur_pos}")

        #     cur_pos = found_cursor.position()
        # maximumImageWidth = self.width() - 32

        # self.removeUnusedResources()

        # resize pictures to match the max width
        # print("TEXT RESIZE EVENT")
        # print(self.images)
        # for uuid in self.images.keys():
        #     print(uuid)
        #     img = self.images[uuid]
        #     # img = QTextImageFormat()
        #     img.setName(uuid)
        #     editorMaxWidth = self.width() - 32
        #     print(f"before: {img.width()} vs. {editorMaxWidth}")

        #     # if img.width() > editorMaxWidth:
        #     print("resizing")
        #     print(f"before: {img.width()} vs. {editorMaxWidth}")
        #     img.setWidth(editorMaxWidth)
        # img.width()

        super().resizeEvent(e)

    def removeUnusedResources(self):
        uuidToRemove = []

        for uuid in self.images.keys():

            resource = self.document().resource(QTextDocument.ImageResource, QUrl(uuid))

            if resource == None:
                uuidToRemove.append(uuid)
                # del self.images[uuid]
                continue

            # self.addImageResource(self.images[uuid])

        for uuid in uuidToRemove:
            del self.images[uuid]

    def addImageResource(self, ImageResource: QImage, uuid=hexuuid()):
        # cases:
        # pasted image: uuid = generated from hash
        # local file draged: uuid = file path
        if uuid == "":
            raise ValueError("provided 'uuid' is empty")

        print("INSERTING IMAGE")

        maximumImageWidth = self.minimumWidth() - 32
        maximumImageHeight = 400 - 32
        print(maximumImageWidth)
        # if width >= maximumImageWidth:
        # conssider padding
        # factor = maximumImageWidth / widthv <-
        # width *= factor <-
        # height *= factor

        # print(resource.value())
        width = ImageResource.width()

        if width > maximumImageWidth:
            print("SCALING TO WIDTH")
            print(f"{width} : {maximumImageWidth}")
            ImageResource = ImageResource.scaledToWidth(
                math.floor(maximumImageWidth), Qt.SmoothTransformation
            )

        height = ImageResource.height()

        if height > maximumImageHeight:
            print("SCALING TO HEIGHT")
            print(f"{height} : {maximumImageHeight}")
            ImageResource = ImageResource.scaledToHeight(
                math.floor(maximumImageHeight), Qt.SmoothTransformation
            )
        # sc_resource.setDotsPerMeterX(self.DPM);
        # sc_resource.setDotsPerMeterY(self.DPM);

        resourcePath = f"{self.parent_.dir}/{self.parent_.baseName}"

        if not os.path.exists(resourcePath):
            os.mkdir(resourcePath)

        image_name = f"{resourcePath}/{uuid}.png"

        # ImageResource.
        ImageResource.save(image_name)

        # textImageFormat = QTextImageFormat()
        # textImageFormat.setName(image_name)
        # if width > maximumImageWidth:
        #     textImageFormat.setWidth(maximumImageWidth)
        # else:
        #     textImageFormat.setWidth(width)

        self.document().addResource(
            QTextDocument.ImageResource, QUrl(image_name), ImageResource
        )

        self.images[image_name] = ImageResource
        # self.images[uuid] = textImageFormat

        return image_name
        # return uuid

    def setCurrentFont(self, font: QFont):
        print(f"Setting Current Font: {font.family()}")
        # Update the default format with the new font
        self.defaultCharFormat.setFont(font)

        # Get current cursor
        cursor = self.textCursor()

        # Create a format with all font properties
        char_fmt = QTextCharFormat()
        char_fmt.setFont(font)

        if cursor.hasSelection():
            # If text is selected, apply format to selection
            cursor.beginEditBlock()
            cursor.mergeCharFormat(char_fmt)
            cursor.endEditBlock()
            self.setTextCursor(cursor)
        else:
            # For cursor without selection, set format for future typing
            cursor.setCharFormat(char_fmt)
            self.setTextCursor(cursor)

            # Also update document default font for consistency
            self.document().setDefaultFont(font)

        # Call parent implementation for proper handling
        super().setCurrentFont(font)
        self.setFocus()
        #     doc = self.document()
        #     doc_fmt = doc.defaultTextOption()
        #     new_doc_fmt = QTextOption(doc_fmt)
        #     self.document().setDefaultFont(font)

        # # Call the parent implementation for non-selected text
        # super().setCurrentFont(font)
        # self.setFocus()
