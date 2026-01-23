#!/usr/bin/env python3
"""
RePhraser main entry point.

This module provides the main entry point for the RePhraser application.
It sets up the PyQt5 application with dark theme and launches the main window.
"""

import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDir

from rephraser.lib.DarkPallete import DarkPalette
from rephraser.RePhraser import MainWindow
from rephraser import ICON_PATH, STYLESHEET_PATH, get_version


def setup_application() -> QApplication:
    """Initialize and configure the QApplication with dark theme."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("RePhraser")
    app.setApplicationVersion(get_version())
    app.setOrganizationName("EliazarInso")
    app.setApplicationDisplayName("RePhraser")
    
    # Set Fusion style for better cross-platform appearance
    fusion_style = QStyleFactory.create("Fusion")
    if fusion_style:
        app.setStyle(fusion_style)
    
    # Apply dark palette
    dark_palette = DarkPalette()
    app.setPalette(dark_palette)
    
    # Load and apply stylesheet
    if STYLESHEET_PATH.exists():
        with open(STYLESHEET_PATH, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Stylesheet not found at {STYLESHEET_PATH}")
    
    # Set application icon
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    else:
        print(f"Warning: Icon not found at {ICON_PATH}")
    
    return app


def main():
    """Main entry point for the RePhraser application."""
    try:
        # Create and setup application
        app = setup_application()
        
        # Create and show main window
        window = MainWindow()
        
        # Set window icon (fallback if app icon failed)
        if ICON_PATH.exists():
            window.setWindowIcon(QIcon(str(ICON_PATH)))
        
        window.show()
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error starting RePhraser: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()