"""
RePhraser - A text editing application with author attribution and formatting tools.

This package provides a PyQt5-based rich text editor with multi-author support,
allowing different authors to be visually distinguished through color coding
and formatting attribution.
"""

import os
from pathlib import Path

__version__ = "0.0.2"
__author__ = "EliazarInso"
__email__ = "deadbush225@gmail.com"
__description__ = "Rephrase essays and collage texts"

# Base directory for the package
_base_dir = Path(__file__).parent.resolve()
basedir = _base_dir

# Project root directory (two levels up from src/rephraser)
project_dir = _base_dir.parents[1]

# Resource paths
RESOURCES_DIR = basedir
ICON_PATH = basedir / "Rephraser.ico" 
STYLESHEET_PATH = basedir / "dark.qss"
IMAGES_DIR = basedir / "images"

def get_resource_path(filename: str) -> Path:
    """Get the full path to a resource file in the package directory."""
    return basedir / filename

def get_version() -> str:
    """Return the current version of RePhraser."""
    return __version__
