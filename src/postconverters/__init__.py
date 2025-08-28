"""
Módulo de postconversores para el sistema de conversión de imágenes TIFF.

Los postconversores se ejecutan después de la conversión principal para realizar
tareas adicionales como generación de metadatos METS y consolidación de PDFs.
"""

from .base import BasePostConverter
from .met_format_postconverter import METFormatPostConverter
from .consolidated_pdf_postconverter import ConsolidatedPDFPostconverter

__all__ = [
    "BasePostConverter",
    "METFormatPostConverter", 
    "ConsolidatedPDFPostconverter"
]
