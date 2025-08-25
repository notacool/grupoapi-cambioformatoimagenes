"""
Módulo de conversores para diferentes formatos de imagen
"""

from .base import BaseConverter
from .jpg_resolution_converter import JPGResolutionConverter
from .met_metadata_converter import METMetadataConverter
from .pdf_easyocr_converter import PDFEasyOCRConverter

__all__ = [
    "BaseConverter",
    "JPGResolutionConverter",
    "PDFEasyOCRConverter",
    "METMetadataConverter",
]
