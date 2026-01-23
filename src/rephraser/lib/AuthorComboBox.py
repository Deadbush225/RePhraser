from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from rephraser.lib.Logger import Logger
from rephraser.lib.ClickableLabel import ClickableLabel
from rephraser.lib.AuthorEntry import AuthorEntry
from rephraser.lib.Stores import store
from rephraser.lib.DarkPallete import enable_dark_titlebar


class AuthorItemDelegate(QStyledItemDelegate):
    """Custom delegate to render author items with their formatting"""
    
    def paint(self, painter, option, index):
        # Get author name and properties
        author_name = index.data(Qt.DisplayRole)
        
        if author_name == "None":
            # Use default rendering for "None" option
            super().paint(painter, option, index)
            return
        
        # Get author properties from store
        if author_name not in store.author_dictionary:
            super().paint(painter, option, index)
            return
        
        props = store.author_dictionary[author_name]
        
        # Set up painter
        painter.save()
        
        # Draw background
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            painter.fillRect(option.rect, QColor(props["background"]))
        
        # Set up font
        font = QFont("Lexend", 11)
        font.setItalic(props["italic"])
        
        # Convert weight to Qt font weight
        weight_value = props["weight"]
        if weight_value >= 90:
            font.setWeight(QFont.Black)
        elif weight_value >= 70:
            font.setWeight(QFont.Bold)
        elif weight_value >= 55:
            font.setWeight(QFont.DemiBold)
        elif weight_value >= 35:
            font.setWeight(QFont.Normal)
        else:
            font.setWeight(QFont.Light)
        
        painter.setFont(font)
        
        # Set text color
        if option.state & QStyle.State_Selected:
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(QColor(props["foreground"]))
        
        # Draw text centered
        text_rect = option.rect.adjusted(4, 2, -4, -2)
        painter.drawText(text_rect, Qt.AlignCenter, author_name)
        
        painter.restore()
    
    def sizeHint(self, option, index):
        """Return appropriate size for items"""
        return QSize(200, 30)


class AuthorComboBox(QComboBox):
    """Custom ComboBox for selecting authors with styled labels"""
    
    author_changed = pyqtSignal(str)  # Signal emitted when author changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_ = parent
        self.settings = QSettings("DeadBush225", "RePhraser")
        
        # Set custom delegate for styling
        self.setItemDelegate(AuthorItemDelegate())
        
        # Set minimum height for better appearance
        self.setMinimumHeight(35)
        
        # Load author dictionary from settings
        store.author_dictionary = self.settings.value("authors")
        
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
        
        self.populateComboBox()
        
        # Connect signals
        self.currentTextChanged.connect(self.onAuthorChanged)
    
    def paintEvent(self, event):
        """Custom paint event to show current selection with author styling"""
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))
        
        # Draw the combobox frame and arrow
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        
        # Get current text
        current_text = self.currentText()
        
        if current_text != "None" and current_text in store.author_dictionary:
            # Apply author styling to the current selection display
            props = store.author_dictionary[current_text]
            
            # Set background color
            opt.palette.setColor(QPalette.Button, QColor(props["background"]))
            opt.palette.setColor(QPalette.ButtonText, QColor(props["foreground"]))
            
            # Draw combo box with custom colors
            painter.drawComplexControl(QStyle.CC_ComboBox, opt)
            
            # Draw the text with custom font
            font = QFont("Lexend", 11)
            font.setItalic(props["italic"])
            
            weight_value = props["weight"]
            if weight_value >= 90:
                font.setWeight(QFont.Black)
            elif weight_value >= 70:
                font.setWeight(QFont.Bold)
            elif weight_value >= 55:
                font.setWeight(QFont.DemiBold)
            elif weight_value >= 35:
                font.setWeight(QFont.Normal)
            else:
                font.setWeight(QFont.Light)
            
            painter.setFont(font)
            painter.setPen(QColor(props["foreground"]))
            
            # Calculate text rect (avoiding the arrow area)
            text_rect = self.style().subControlRect(QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxEditField, self)
            text_rect.adjust(4, 0, -4, 0)
            
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, current_text)
        else:
            # Default rendering for "None" and other cases
            painter.drawComplexControl(QStyle.CC_ComboBox, opt)
            painter.drawControl(QStyle.CE_ComboBoxLabel, opt)
    
    def populateComboBox(self):
        """Populate the combo box with authors"""
        current_selection = self.currentText()
        self.clear()
        
        # Add "None" as default option
        self.addItem("None")
        
        # Add all authors from dictionary
        for author_name in store.author_dictionary.keys():
            self.addItem(author_name)
        
        # Restore selection if it still exists
        if current_selection and current_selection != "":
            index = self.findText(current_selection)
            if index >= 0:
                self.setCurrentIndex(index)
            else:
                self.setCurrentIndex(0)  # Default to "None"
        
        # Force a repaint to update styling
        self.update()
    
    def onAuthorChanged(self, author_name):
        """Handle author selection change"""
        if author_name == "None":
            # Reset to default format
            if self.parent_ and hasattr(self.parent_, 'editor'):
                self.parent_.editor.resetToDefaultFormat()
        else:
            # Apply author format
            if self.parent_ and hasattr(self.parent_, 'editor'):
                self.parent_.editor.setDefaultCharFormat(author_name)
        
        # Trigger repaint to update styling
        self.update()
        self.author_changed.emit(author_name)
    
    def addAuthor(self, author_name=""):
        """Show dialog to add new author"""
        new_entry = AuthorEntry(author_name=author_name)
        
        if author_name and author_name in store.author_dictionary:
            # Editing existing author
            props = store.author_dictionary[author_name]
            new_entry.foreground = QColor(props["foreground"])
            new_entry.background = QColor(props["background"])
            new_entry.italic = props["italic"]
            new_entry.weight = props["weight"]
            new_entry.href = props["href"]
        
        dialog = AddAuthorDialog(new_entry, parent=self)
        dialog.submit.connect(self.onAuthorAdded)
        
        enable_dark_titlebar(dialog)
        dialog.exec_()
    
    def onAuthorAdded(self, entry):
        """Handle new author being added"""
        store.author_dictionary[entry.author_name] = entry.getProperties()
        self.saveSettings()
        self.populateComboBox()
        
        # Select the newly added author
        index = self.findText(entry.author_name)
        if index >= 0:
            self.setCurrentIndex(index)
        
        # Update display
        self.update()
    
    def removeCurrentAuthor(self):
        """Remove currently selected author"""
        current_author = self.currentText()
        if current_author != "None" and current_author in store.author_dictionary:
            reply = QMessageBox.question(
                self, 
                "Remove Author",
                f"Are you sure you want to remove '{current_author}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                store.author_dictionary.pop(current_author)
                self.saveSettings()
                self.populateComboBox()
                self.setCurrentIndex(0)  # Reset to "None"
    
    def saveSettings(self):
        """Save author dictionary to settings"""
        self.settings.setValue("authors", store.author_dictionary)


class AddAuthorDialog(QDialog):
    """Dialog for adding/editing authors"""
    
    submit = pyqtSignal(AuthorEntry)

    def __init__(self, entry, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Author")
        
        p = entry.getProperties(include_name=True)
        
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

        # Author name
        author_cont = QHBoxLayout()
        author_cont.addWidget(QLabel("Author Name: "))
        self.author_field = QLineEdit(author_name)
        author_cont.addWidget(self.author_field)

        # Foreground color
        foreground_cont = QHBoxLayout()
        foreground_cont.addWidget(QLabel("Foreground: "))
        self.colorPrev_foreground = ClickableLabel(QColor(foreground))
        foreground_cont.addWidget(self.colorPrev_foreground)

        # Background color
        background_cont = QHBoxLayout()
        background_cont.addWidget(QLabel("Background: "))
        self.colorPrev_background = ClickableLabel(QColor(background))
        background_cont.addWidget(self.colorPrev_background)

        # Weight
        weight_cont = QHBoxLayout()
        weight_cont.addWidget(QLabel("Weight: "))
        self.weight_spinbox = QSpinBox()
        self.weight_spinbox.setMinimum(0)
        self.weight_spinbox.setMaximum(100)
        self.weight_spinbox.setSingleStep(10)
        self.weight_spinbox.setValue(weight)
        weight_cont.addWidget(self.weight_spinbox)

        # Formatting options
        formatting_cont = QHBoxLayout()
        self.isItalic = QCheckBox("Italic")
        self.isItalic.setChecked(italic)
        formatting_cont.addWidget(self.isItalic)

        # Href
        href_cont = QHBoxLayout()
        href_cont.addWidget(QLabel("Href: "))
        self.href_field = QLineEdit()
        self.href_field.setText(href)
        href_cont.addWidget(self.href_field)

        # Buttons
        button_layout = QHBoxLayout()
        self.saveAuthor_btn = QPushButton("Save Author")
        self.saveAuthor_btn.clicked.connect(self.fin)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.saveAuthor_btn)

        # Add all layouts
        mainlayout.addLayout(author_cont)
        mainlayout.addLayout(foreground_cont)
        mainlayout.addLayout(background_cont)
        mainlayout.addLayout(weight_cont)
        mainlayout.addLayout(formatting_cont)
        mainlayout.addLayout(href_cont)
        mainlayout.addLayout(button_layout)

        self.setLayout(mainlayout)

    def fin(self):
        """Finalize and emit the author entry"""
        author_name = self.author_field.text()
        
        if not author_name.strip():
            QMessageBox.warning(self, "Invalid Name", "Please enter a valid author name.")
            return
            
        color = self.colorPrev_foreground.color.name(QColor.HexArgb)
        background = self.colorPrev_background.color.name(QColor.HexArgb)
        weight = self.weight_spinbox.value()
        italic = self.isItalic.isChecked()
        href = self.href_field.text()

        self.accept()
        self.submit.emit(
            AuthorEntry(author_name, color, background, weight, italic, href)
        )