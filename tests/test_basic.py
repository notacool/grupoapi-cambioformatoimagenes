#!/usr/bin/env python3
"""
Test básico para verificar imports sin emojis
"""

def test_imports():
    """Test básico de imports"""
    try:
        from src.converter import TIFFConverter
        print("TIFFConverter importado correctamente")

        from src.config_manager import ConfigManager
        print("ConfigManager importado correctamente")

        from src.file_processor import FileProcessor
        print("FileProcessor importado correctamente")

        from src.converters import JPGResolutionConverter, PDFEasyOCRConverter, METMetadataConverter
        print("Converters importados correctamente")

        from src.converters.pdf_compressor import PDFCompressor
        print("PDFCompressor importado correctamente")

        from src.postconverters import METFormatPostConverter, ConsolidatedPDFPostconverter
        print("Postconverters importados correctamente")

        print("Todos los imports exitosos")
        return True

    except ImportError as e:
        print(f"Error de import: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

if __name__ == "__main__":
    import sys
    test_success = test_imports()
    if test_success:
        print("Test completado exitosamente")
    else:
        print("Test falló")
        sys.exit(1)
