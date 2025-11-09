from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os

FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]


class Toolbar(QToolBar):
    def reset_toolbar_positions(self):
        """Reset all toolbars to their default positions"""
        main_window = self.parent()

        # First, remove all toolbars from the main window
        main_window.removeToolBar(self)
        main_window.removeToolBar(self.edit_toolbar)
        main_window.removeToolBar(self.format_toolbar)

        # Then add them back in the default positions/areas
        main_window.addToolBar(Qt.TopToolBarArea, self)
        main_window.addToolBar(Qt.TopToolBarArea, self.edit_toolbar)
        main_window.addToolBar(Qt.TopToolBarArea, self.format_toolbar)

        # Make sure they're visible
        self.show()
        self.edit_toolbar.show()
        self.format_toolbar.show()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent().addToolBar(self)
        self.setIconSize(QSize(24, 24))
        file_menu = self.parent().menuBar().addMenu("&File")

        open_file_action = QAction(
            QIcon(":/icons/blue-folder-open-document.png"),
            "Open file...",
            self.parent(),
        )
        open_file_action.setStatusTip("Open file")
        open_file_action.setShortcut(QKeySequence.Open)
        open_file_action.triggered.connect(self.parent().file_open)
        file_menu.addAction(open_file_action)
        self.addAction(open_file_action)

        save_file_action = QAction(QIcon(":/icons/disk.png"), "Save", self.parent())
        save_file_action.setStatusTip("Save current page")
        save_file_action.setShortcut(QKeySequence.Save)
        save_file_action.triggered.connect(self.parent().file_save)
        file_menu.addAction(save_file_action)
        self.addAction(save_file_action)

        saveas_file_action = QAction(
            QIcon(":/icons/disk--pencil.png"),
            "Save As...",
            self.parent(),
        )
        saveas_file_action.setStatusTip("Save current page to specified file")
        saveas_file_action.setShortcut(QKeySequence.SaveAs)
        saveas_file_action.triggered.connect(self.parent().file_saveas)
        file_menu.addAction(saveas_file_action)
        self.addAction(saveas_file_action)

        print_action = QAction(
            QIcon(":/icons/printer.png"),
            "Print...",
            self.parent(),
        )
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.parent().file_print)
        file_menu.addAction(print_action)
        self.addAction(print_action)

        self.edit_toolbar = QToolBar("Edit")
        self.edit_toolbar.setIconSize(QSize(24, 24))
        self.parent().addToolBar(self.edit_toolbar)
        edit_menu = self.parent().menuBar().addMenu("&Edit")

        undo_action = QAction(
            QIcon(":/icons/arrow-curve-180-left.png"),
            "Undo",
            self.parent(),
        )
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.parent().editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(
            QIcon(":/icons/arrow-curve.png"),
            "Redo",
            self.parent(),
        )
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.parent().editor.redo)
        self.edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(":/icons/scissors.png"), "Cut", self.parent())
        cut_action.setStatusTip("Cut selected text")
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.parent().editor.cut)
        self.edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction(
            QIcon(":/icons/document-copy.png"),
            "Copy",
            self.parent(),
        )
        copy_action.setStatusTip("Copy selected text")
        cut_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.parent().editor.copy)
        self.edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction(
            QIcon(":/icons/clipboard-paste-document-text.png"),
            "Paste",
            self.parent(),
        )
        paste_action.setStatusTip("Paste from clipboard")
        cut_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.parent().editor.paste)
        self.edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        select_action = QAction(
            QIcon(":/icons/selection-input.png"),
            "Select all",
            self.parent(),
        )
        select_action.setStatusTip("Select all text")
        cut_action.setShortcut(QKeySequence.SelectAll)
        select_action.triggered.connect(self.parent().editor.selectAll)
        edit_menu.addAction(select_action)

        edit_menu.addSeparator()

        wrap_action = QAction(
            QIcon(":/icons/arrow-continue.png"),
            "Wrap text to window",
            self.parent(),
        )
        wrap_action.setStatusTip("Toggle wrap text to window")
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.parent().edit_toggle_wrap)
        edit_menu.addAction(wrap_action)

        self.format_toolbar = QToolBar("Format")
        self.format_toolbar.setIconSize(QSize(24, 24))
        self.parent().addToolBar(self.format_toolbar)
        format_menu = self.parent().menuBar().addMenu("&Format")

        # We need references to these actions/settings to update as selection changes, so attach to self.parent().
        self.parent().fonts = QFontComboBox()
        self.parent().fonts.currentFontChanged.connect(
            self.parent().editor.setCurrentFont
        )
        font = QFont("Lexend", 12)
        self.parent().fonts.setCurrentFont(font)
        self.parent().editor.setFont(
            font
        )  # needed, since line above doesn't fire "currentFontChanged"

        self.format_toolbar.addWidget(self.parent().fonts)

        self.parent().fontsize = QComboBox()
        self.parent().fontsize.addItems([str(s) for s in FONT_SIZES])

        # Connect to the signal producing the text of the current selection. Convert the string to float
        # and set as the pointsize. We could also use the index + retrieve from FONT_SIZES.
        self.parent().fontsize.currentIndexChanged[str].connect(
            self.update_size
            # lambda s: self.parent().editor.setFontPointSize(float(s))
        )
        self.format_toolbar.addWidget(self.parent().fontsize)

        bold_image = QImage(":/icons/edit-bold.png")
        bold_image.invertPixels()
        bold_pixmap = QPixmap.fromImage(bold_image)

        self.parent().bold_action = QAction(QIcon(bold_pixmap), "Bold", self.parent())
        self.parent().bold_action.setStatusTip("Bold")
        self.parent().bold_action.setShortcut(QKeySequence.Bold)
        self.parent().bold_action.setCheckable(True)
        self.parent().bold_action.toggled.connect(
            lambda x: self.parent().editor.setFontWeight(
                QFont.Bold if x else QFont.Normal
            )
        )
        self.format_toolbar.addAction(self.parent().bold_action)
        format_menu.addAction(self.parent().bold_action)

        italic_image = QImage(":/icons/edit-italic.png")
        italic_image.invertPixels()
        italic_pixmap = QPixmap.fromImage(italic_image)

        self.parent().italic_action = QAction(
            QIcon(italic_pixmap), "Italic", self.parent()
        )
        self.parent().italic_action.setStatusTip("Italic")
        self.parent().italic_action.setShortcut(QKeySequence.Italic)
        self.parent().italic_action.setCheckable(True)
        self.parent().italic_action.toggled.connect(self.parent().editor.setFontItalic)
        self.format_toolbar.addAction(self.parent().italic_action)
        format_menu.addAction(self.parent().italic_action)

        underline_image = QImage(":/icons/edit-underline.png")
        underline_image.invertPixels()
        underline_pixmap = QPixmap.fromImage(underline_image)

        self.parent().underline_action = QAction(
            QIcon(underline_pixmap), "Underline", self.parent()
        )
        self.parent().underline_action.setStatusTip("Underline")
        self.parent().underline_action.setShortcut(QKeySequence.Underline)
        self.parent().underline_action.setCheckable(True)
        self.parent().underline_action.toggled.connect(
            self.parent().editor.setFontUnderline
        )
        self.format_toolbar.addAction(self.parent().underline_action)
        format_menu.addAction(self.parent().underline_action)

        format_menu.addSeparator()

        alignl_image = QImage(":/icons/edit-alignment.png")
        alignl_image.invertPixels()
        alignl_pixmap = QPixmap.fromImage(alignl_image)

        self.parent().alignl_action = QAction(
            QIcon(alignl_pixmap), "Align left", self.parent()
        )
        self.parent().alignl_action.setStatusTip("Align text left")
        self.parent().alignl_action.setCheckable(True)
        self.parent().alignl_action.triggered.connect(
            lambda: self.parent().editor.setAlignment(Qt.AlignLeft)
        )
        self.format_toolbar.addAction(self.parent().alignl_action)
        format_menu.addAction(self.parent().alignl_action)

        alignc_image = QImage(":/icons/edit-alignment-center.png")
        alignc_image.invertPixels()
        alignc_pixmap = QPixmap.fromImage(alignc_image)

        self.parent().alignc_action = QAction(
            QIcon(alignc_pixmap), "Align center", self.parent()
        )
        self.parent().alignc_action.setStatusTip("Align text center")
        self.parent().alignc_action.setCheckable(True)
        self.parent().alignc_action.triggered.connect(
            lambda: self.parent().editor.setAlignment(Qt.AlignCenter)
        )
        self.format_toolbar.addAction(self.parent().alignc_action)
        format_menu.addAction(self.parent().alignc_action)

        alignr_image = QImage(":/icons/edit-alignment-right.png")

        alignr_image.invertPixels()
        alignr_pixmap = QPixmap.fromImage(alignr_image)

        self.parent().alignr_action = QAction(
            QIcon(alignr_pixmap), "Align right", self.parent()
        )
        self.parent().alignr_action.setStatusTip("Align text right")
        self.parent().alignr_action.setCheckable(True)
        self.parent().alignr_action.triggered.connect(
            lambda: self.parent().editor.setAlignment(Qt.AlignRight)
        )
        self.format_toolbar.addAction(self.parent().alignr_action)
        format_menu.addAction(self.parent().alignr_action)

        alignj_image = QImage(":/icons/edit-alignment-justify.png")

        alignj_image.invertPixels()
        alignj_pixmap = QPixmap.fromImage(alignj_image)

        self.parent().alignj_action = QAction(
            QIcon(alignj_pixmap), "Justify", self.parent()
        )
        self.parent().alignj_action.setStatusTip("Justify text")
        self.parent().alignj_action.setCheckable(True)
        self.parent().alignj_action.triggered.connect(
            lambda: self.parent().editor.setAlignment(Qt.AlignJustify)
        )
        self.format_toolbar.addAction(self.parent().alignj_action)
        format_menu.addAction(self.parent().alignj_action)

        format_group = QActionGroup(self.parent())
        format_group.setExclusive(True)
        format_group.addAction(self.parent().alignl_action)
        format_group.addAction(self.parent().alignc_action)
        format_group.addAction(self.parent().alignr_action)
        format_group.addAction(self.parent().alignj_action)

        format_menu.addSeparator()

        # A list of all format-related widgets/actions, so we can disable/enable signals when updating.
        self.parent()._format_actions = [
            self.parent().fonts,
            self.parent().fontsize,
            self.parent().bold_action,
            self.parent().italic_action,
            self.parent().underline_action,
            # We don't need to disable signals for alignment, as they are paragraph-wide.
        ]

        # At the end of your __init__ method
        self.set_scaled_icons()

        view_menu = self.parent().menuBar().addMenu("&View")

        reset_view_action = QAction(
            QIcon(""),
            "Reset View",
            self.parent(),
        )
        reset_view_action.setStatusTip("Reset View")
        reset_view_action.triggered.connect(
            lambda: (self.parent().createDock(), self.reset_toolbar_positions())
        )
        view_menu.addAction(reset_view_action)

        self.parent().editor.cursorPositionChanged.connect(self.update_format)

    def update_size(self, s: float):
        editor = self.parent().editor
        sizef = float(s)

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

        # Update document default font so new text also matches
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
        """Update the formatting toolbar/actions when the cursor position changes"""
        # Disable signals to avoid triggering format changes while updating UI
        self.block_signals(self.parent()._format_actions, True)

        # Get the current format at cursor position
        cursor = self.parent().editor.textCursor()
        char_format = cursor.charFormat()

        # Update font selector
        current_font = char_format.font()
        self.parent().fonts.setCurrentFont(current_font)

        # Update font size
        font_size = char_format.fontPointSize()
        if font_size > 0:  # fontPointSize returns 0 if not set
            size_index = -1
            for i, size in enumerate(FONT_SIZES):
                if size == int(font_size):
                    size_index = i
                    break
            if size_index >= 0:
                self.parent().fontsize.setCurrentIndex(size_index)

        # Update bold button
        self.parent().bold_action.setChecked(current_font.weight() >= QFont.Bold)

        # Update italic button
        self.parent().italic_action.setChecked(current_font.italic())

        # Update underline button
        self.parent().underline_action.setChecked(current_font.underline())

        # Update alignment buttons (paragraph-wide formatting)
        block_format = cursor.blockFormat()
        alignment = block_format.alignment()

        self.parent().alignl_action.setChecked(alignment == Qt.AlignLeft)
        self.parent().alignc_action.setChecked(alignment == Qt.AlignCenter)
        self.parent().alignr_action.setChecked(alignment == Qt.AlignRight)
        self.parent().alignj_action.setChecked(alignment == Qt.AlignJustify)

        # Re-enable signals
        self.block_signals(self.parent()._format_actions, False)

    # Add this function to your Toolbar class
    def set_scaled_icons(self):
        # Enable icon scaling
        for toolbar in [
            self.actions(),
            self.edit_toolbar.actions(),
            self.format_toolbar.actions(),
        ]:
            for action in toolbar:
                if action.icon().isNull():
                    continue

                # Get the original icon
                icon = action.icon()
                pixmap = icon.pixmap(QSize(16, 16))

                # Create a scaled version
                scaled_pixmap = pixmap.scaled(
                    QSize(24, 24),  # Target size
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )

                # Set the scaled icon
                action.setIcon(QIcon(scaled_pixmap))
