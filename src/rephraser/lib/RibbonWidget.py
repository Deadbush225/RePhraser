from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from rephraser.lib.AuthorComboBox import AuthorComboBox
import os


FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]


class RibbonTab(QWidget):
    """Base class for ribbon tabs"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.root = QVBoxLayout(self)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 3, 5, 3)  # Reduced margins
        self.layout.setSpacing(8)  # Reduced spacing
        # self.root.addLayout(self.layout)
        # self.root.addStretch()
        
        
    def add_group(self, title, widgets):
        """Add a group of widgets with a title"""
        group_widget = QWidget()
        group_widget.setObjectName("ribbon_group")
        group_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        group_layout = QVBoxLayout(group_widget)
        group_layout.setContentsMargins(3, 2, 3, 2)  # Minimal margins
        
        # Add title
        title_label = QLabel(title)
        title_label.setObjectName("ribbon_group_title")
        title_label.setStyleSheet("color: #c3c3c3;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(25)
        
        # Create content layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(2)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add widgets
        for widget in widgets:
            if isinstance(widget, QAction):
                # Convert QAction to QPushButton for ribbon interface
                button = QPushButton()
                button.setObjectName("ribbon_button")
                button.setIcon(widget.icon())
                button.setToolTip(widget.statusTip())
                button.setIconSize(QSize(20, 20))  # Reduced from 24, 24
                button.setFixedSize(32, 32)  # Reduced from 32, 32
                button.setCheckable(widget.isCheckable())
                button.clicked.connect(widget.trigger)
                
                # Store references for checkable buttons
                if hasattr(self, 'main_window'):
                    if widget == getattr(self.main_window, 'bold_action', None):
                        self.bold_button = button
                    elif widget == getattr(self.main_window, 'italic_action', None):
                        self.italic_button = button
                    elif widget == getattr(self.main_window, 'underline_action', None):
                        self.underline_button = button
                
                content_layout.addWidget(button)
            else:
                content_layout.addWidget(widget)
        
        group_layout.addWidget(title_label)
        group_layout.addLayout(content_layout)
        # Remove the addStretch() to minimize height
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(1)
        # border-left: 1px solid #212121;
        # border-right: 1px solid #4b4b4b;
        # max-width: 0px;
        separator.setStyleSheet("""QFrame {
        background-color: #535353;       
    }""")  # Reduced margin from 5px
        
        self.layout.addWidget(group_widget)
        self.layout.addWidget(separator)

class EditTab(RibbonTab):
    """Edit tab containing file operations and text editing tools"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # File operations group
        file_actions = []
        
        # Create file actions
        open_action = QAction(QIcon(":/icons/blue-folder-open-document.png"), "Open", self)
        open_action.setStatusTip("Open file")
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.main_window.file_open)
        file_actions.append(open_action)
        
        save_action = QAction(QIcon(":/icons/disk.png"), "Save", self)
        save_action.setStatusTip("Save current page")
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.main_window.file_save)
        file_actions.append(save_action)
        
        saveas_action = QAction(QIcon(":/icons/disk--pencil.png"), "Save As", self)
        saveas_action.setStatusTip("Save current page to specified file")
        saveas_action.setShortcut(QKeySequence.SaveAs)
        saveas_action.triggered.connect(self.main_window.file_saveas)
        file_actions.append(saveas_action)
        
        print_action = QAction(QIcon(":/icons/printer.png"), "Print", self)
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.main_window.file_print)
        file_actions.append(print_action)
        
        self.add_group("File", file_actions)
        
        # Edit operations group
        edit_actions = []
        
        undo_action = QAction(QIcon(":/icons/arrow-curve-180-left.png"), "Undo", self)
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.main_window.editor.undo)
        edit_actions.append(undo_action)
        
        redo_action = QAction(QIcon(":/icons/arrow-curve.png"), "Redo", self)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.main_window.editor.redo)
        edit_actions.append(redo_action)
        
        cut_action = QAction(QIcon(":/icons/scissors.png"), "Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.main_window.editor.cut)
        edit_actions.append(cut_action)
        
        copy_action = QAction(QIcon(":/icons/document-copy.png"), "Copy", self)
        copy_action.setStatusTip("Copy selected text")
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.main_window.editor.copy)
        edit_actions.append(copy_action)
        
        paste_action = QAction(QIcon(":/icons/clipboard-paste-document-text.png"), "Paste", self)
        paste_action.setStatusTip("Paste from clipboard")
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.main_window.editor.paste)
        edit_actions.append(paste_action)
        
        self.add_group("Edit", edit_actions)
        
        # Format group
        format_widgets = []
        
        # Font family
        self.main_window.fonts = QFontComboBox()
        self.main_window.fonts.currentFontChanged.connect(self.update_fontFamily)
        font = QFont("Lexend", 12)
        self.main_window.fonts.setCurrentFont(font)
        self.main_window.editor.setFont(font)
        format_widgets.append(self.main_window.fonts)
        
        # Font size
        self.main_window.fontsize = QComboBox()
        self.main_window.fontsize.addItems([str(s) for s in FONT_SIZES])
        self.main_window.fontsize.currentIndexChanged[str].connect(self.update_size)
        format_widgets.append(self.main_window.fontsize)
        
        self.add_group("Font", format_widgets)
        
        # Text style group
        style_actions = []
        
        bold_image = QImage(":/icons/edit-bold.png")
        bold_image.invertPixels()
        bold_pixmap = QPixmap.fromImage(bold_image)
        
        self.main_window.bold_action = QAction(QIcon(bold_pixmap), "Bold", self)
        self.main_window.bold_action.setStatusTip("Bold")
        self.main_window.bold_action.setShortcut(QKeySequence.Bold)
        self.main_window.bold_action.setCheckable(True)
        self.main_window.bold_action.toggled.connect(self.update_weight)
        style_actions.append(self.main_window.bold_action)
        
        italic_image = QImage(":/icons/edit-italic.png")
        italic_image.invertPixels()
        italic_pixmap = QPixmap.fromImage(italic_image)
        
        self.main_window.italic_action = QAction(QIcon(italic_pixmap), "Italic", self)
        self.main_window.italic_action.setStatusTip("Italic")
        self.main_window.italic_action.setShortcut(QKeySequence.Italic)
        self.main_window.italic_action.setCheckable(True)
        self.main_window.italic_action.toggled.connect(self.update_italic)
        style_actions.append(self.main_window.italic_action)
        
        underline_image = QImage(":/icons/edit-underline.png")
        underline_image.invertPixels()
        underline_pixmap = QPixmap.fromImage(underline_image)
        
        self.main_window.underline_action = QAction(QIcon(underline_pixmap), "Underline", self)
        self.main_window.underline_action.setStatusTip("Underline")
        self.main_window.underline_action.setShortcut(QKeySequence.Underline)
        self.main_window.underline_action.setCheckable(True)
        self.main_window.underline_action.toggled.connect(self.update_underline)
        style_actions.append(self.main_window.underline_action)
        
        self.add_group("Style", style_actions)
        
        # Store references to checkable buttons for update_format
        self.bold_button = None
        self.italic_button = None 
        self.underline_button = None
        
        self.add_group("Style", style_actions)
        
        # Alignment group
        align_actions = []
        
        alignl_image = QImage(":/icons/edit-alignment.png")
        alignl_image.invertPixels()
        alignl_pixmap = QPixmap.fromImage(alignl_image)
        
        self.main_window.alignl_action = QAction(QIcon(alignl_pixmap), "Align Left", self)
        self.main_window.alignl_action.setStatusTip("Align text left")
        self.main_window.alignl_action.setCheckable(True)
        self.main_window.alignl_action.triggered.connect(
            lambda: self.main_window.editor.setAlignment(Qt.AlignLeft)
        )
        align_actions.append(self.main_window.alignl_action)
        
        alignc_image = QImage(":/icons/edit-alignment-center.png")
        alignc_image.invertPixels()
        alignc_pixmap = QPixmap.fromImage(alignc_image)
        
        self.main_window.alignc_action = QAction(QIcon(alignc_pixmap), "Align Center", self)
        self.main_window.alignc_action.setStatusTip("Align text center")
        self.main_window.alignc_action.setCheckable(True)
        self.main_window.alignc_action.triggered.connect(
            lambda: self.main_window.editor.setAlignment(Qt.AlignCenter)
        )
        align_actions.append(self.main_window.alignc_action)
        
        alignr_image = QImage(":/icons/edit-alignment-right.png")
        alignr_image.invertPixels()
        alignr_pixmap = QPixmap.fromImage(alignr_image)
        
        self.main_window.alignr_action = QAction(QIcon(alignr_pixmap), "Align Right", self)
        self.main_window.alignr_action.setStatusTip("Align text right")
        self.main_window.alignr_action.setCheckable(True)
        self.main_window.alignr_action.triggered.connect(
            lambda: self.main_window.editor.setAlignment(Qt.AlignRight)
        )
        align_actions.append(self.main_window.alignr_action)
        
        alignj_image = QImage(":/icons/edit-alignment-justify.png")
        alignj_image.invertPixels()
        alignj_pixmap = QPixmap.fromImage(alignj_image)
        
        self.main_window.alignj_action = QAction(QIcon(alignj_pixmap), "Justify", self)
        self.main_window.alignj_action.setStatusTip("Justify text")
        self.main_window.alignj_action.setCheckable(True)
        self.main_window.alignj_action.triggered.connect(
            lambda: self.main_window.editor.setAlignment(Qt.AlignJustify)
        )
        align_actions.append(self.main_window.alignj_action)
        
        # Create alignment group
        format_group = QActionGroup(self.main_window)
        format_group.setExclusive(True)
        format_group.addAction(self.main_window.alignl_action)
        format_group.addAction(self.main_window.alignc_action)
        format_group.addAction(self.main_window.alignr_action)
        format_group.addAction(self.main_window.alignj_action)
        
        self.add_group("Alignment", align_actions)
        
        # Format actions list for signal blocking
        self.main_window._format_actions = [
            self.main_window.fonts,
            self.main_window.fontsize,
            self.main_window.bold_action,
            self.main_window.italic_action,
            self.main_window.underline_action,
        ]
        
        # Connect cursor position change to update format
        self.main_window.editor.cursorPositionChanged.connect(self.update_format)
        
        # Add stretch to push everything to the left
        self.layout.addStretch()
    
    def update_weight(self, is_bold: bool):
        weight = QFont.Bold if is_bold else QFont.Normal
        self.main_window.editor.defaultCharFormat.setFontWeight(weight)
        self.main_window.editor.setFontWeight(weight)

    def update_italic(self, is_italic: bool):
        self.main_window.editor.setFontItalic(is_italic)
        self.main_window.editor.defaultCharFormat.setFontItalic(is_italic)

    def update_underline(self, is_underline: bool):
        self.main_window.editor.setFontUnderline(is_underline)
        self.main_window.editor.defaultCharFormat.setFontUnderline(is_underline)

    def update_fontFamily(self, font: QFont):
        self.main_window.editor.setFontFamily(font.family())
        self.main_window.editor.defaultCharFormat.setFontFamily(font.family())

    def update_size(self, s: str):
        editor = self.main_window.editor
        sizef = float(s)

        # Update the default format
        editor.defaultCharFormat.setFontPointSize(sizef)

        # Save current cursor/selection to restore later
        cur = editor.textCursor()
        had_selection = cur.hasSelection()
        sel_start = cur.selectionStart()
        sel_end = cur.selectionEnd()
        pos = cur.position()

        # Apply the size to the whole document
        doc_cursor = QTextCursor(editor.document())
        doc_cursor.beginEditBlock()
        doc_cursor.select(QTextCursor.Document)
        fmt = QTextCharFormat()
        fmt.setFontPointSize(sizef)
        doc_cursor.mergeCharFormat(fmt)
        doc_cursor.endEditBlock()

        # Update document default font
        default_font = editor.currentFont()
        default_font.setPointSize(int(sizef))
        editor.document().setDefaultFont(default_font)

        # Ensure typing uses the new size
        curr_fmt = editor.currentCharFormat()
        curr_fmt.setFontPointSize(sizef)
        editor.setCurrentCharFormat(curr_fmt)

        # Restore original cursor/selection
        new_cursor = editor.textCursor()
        if had_selection:
            new_cursor.setPosition(sel_start)
            new_cursor.setPosition(sel_end, QTextCursor.KeepAnchor)
        else:
            new_cursor.setPosition(pos)
        editor.setTextCursor(new_cursor)

    def block_signals(self, objects, b):
        for o in objects:
            if hasattr(o, "blockSignals"):
                o.blockSignals(b)

    def update_format(self):
        """Update the formatting when cursor position changes"""
        # Disable signals to avoid triggering format changes while updating UI
        self.block_signals(self.main_window._format_actions, True)

        # Get the current format at cursor position
        cursor = self.main_window.editor.textCursor()
        char_format = cursor.charFormat()

        # Update font selector
        current_font = char_format.font()
        self.main_window.fonts.setCurrentFont(current_font)

        # Update font size
        font_size = char_format.fontPointSize()
        if font_size > 0:
            size_index = -1
            for i, size in enumerate(FONT_SIZES):
                if size == int(font_size):
                    size_index = i
                    break
            if size_index >= 0:
                self.main_window.fontsize.setCurrentIndex(size_index)

        # Update formatting buttons if not modified by author
        if char_format.background() == self.main_window.editor.defaultCharFormat.background():
            is_bold = current_font.weight() >= QFont.Bold
            is_italic = current_font.italic()
            is_underline = current_font.underline()
            
            self.main_window.bold_action.setChecked(is_bold)
            self.main_window.italic_action.setChecked(is_italic)
            self.main_window.underline_action.setChecked(is_underline)
            
            # Update ribbon buttons if they exist
            if hasattr(self, 'bold_button') and self.bold_button:
                self.bold_button.setChecked(is_bold)
            if hasattr(self, 'italic_button') and self.italic_button:
                self.italic_button.setChecked(is_italic)
            if hasattr(self, 'underline_button') and self.underline_button:
                self.underline_button.setChecked(is_underline)

        # Update alignment buttons
        block_format = cursor.blockFormat()
        alignment = block_format.alignment()

        self.main_window.alignl_action.setChecked(alignment == Qt.AlignLeft)
        self.main_window.alignc_action.setChecked(alignment == Qt.AlignCenter)
        self.main_window.alignr_action.setChecked(alignment == Qt.AlignRight)
        self.main_window.alignj_action.setChecked(alignment == Qt.AlignJustify)

        # Re-enable signals
        self.block_signals(self.main_window._format_actions, False)


class AuthorTab(RibbonTab):
    """Author tab containing author selection and management tools"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Author Selection group
        selection_widgets = []
        
        # Author combo box with label
        author_container = QWidget()
        author_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        author_layout = QHBoxLayout(author_container)
        author_layout.setContentsMargins(0, 0, 0, 0)
        author_layout.setSpacing(2)
        
        # author_label = QLabel("Current Author:")
        # author_label.setAlignment(Qt.AlignCenter)
        # author_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.main_window.author_combo = AuthorComboBox(parent=self.main_window)
        self.main_window.author_combo.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.main_window.author_combo.setMinimumWidth(150)
        
        # author_layout.addWidget(author_label)
        author_layout.addWidget(self.main_window.author_combo)
        
        selection_widgets.append(author_container)
        
        self.add_group("Current Author", selection_widgets)
        
        # Author Management group
        management_widgets = []
        
        # Create horizontal layout for buttons
        button_container = QWidget()
        button_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(2)
        
        add_btn = QPushButton("Add Author")
        add_btn.clicked.connect(lambda: self.main_window.author_combo.addAuthor())
        
        edit_btn = QPushButton("Edit Author")
        edit_btn.clicked.connect(
            lambda: self.main_window.author_combo.addAuthor(self.main_window.author_combo.currentText())
            if self.main_window.author_combo.currentText() != "None" else None
        )
        
        remove_btn = QPushButton("Remove Author")
        remove_btn.clicked.connect(self.main_window.author_combo.removeCurrentAuthor)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(remove_btn)
        
        management_widgets.append(button_container)
        
        self.add_group("Management", management_widgets)
        
        # Format Reset group
        reset_widgets = []
        
        reset_btn = QPushButton("Reset Format")
        reset_btn.clicked.connect(lambda: self.main_window.editor.resetToDefaultFormat())
        reset_widgets.append(reset_btn)
        
        self.add_group("Reset", reset_widgets)
        
        # Add stretch to push everything to the left
        self.layout.addStretch()


class RibbonWidget(QWidget):
    """Main ribbon widget containing tabbed interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Create tabs
        self.edit_tab = EditTab(self.main_window)
        self.author_tab = AuthorTab(self.main_window)
        
        # Add tabs
        self.tab_widget.addTab(self.edit_tab, "Edit")
        self.tab_widget.addTab(self.author_tab, "Author")
        
        layout.addWidget(self.tab_widget)
