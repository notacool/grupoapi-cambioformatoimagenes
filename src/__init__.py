"""
Conversor de Archivos TIFF - Módulo principal
"""

from .config_manager import ConfigManager
from .converter import TIFFConverter
from .file_processor import FileProcessor
from .output_manager import OutputManager, output_manager

__all__ = [
    "ConfigManager",
    "TIFFConverter", 
    "FileProcessor",
    "OutputManager",
    "output_manager"
]
