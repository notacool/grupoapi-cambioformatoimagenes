#!/usr/bin/env python3
"""
Test de funcionalidad de compresión de PDF
"""

import tempfile
from pathlib import Path
from src.converters.pdf_compressor import PDFCompressor
from src.output_manager import output_manager

def test_pdf_compressor_init():
    """Test de inicialización del PDFCompressor"""
    try:
        # Configuración básica
        config = {
            "enabled": True,
            "compression_level": "ebook",
            "target_dpi": 200,
            "image_quality": 85,
            "remove_metadata": True,
            "fallback_on_error": True
        }

        compressor = PDFCompressor(config)

        # Verificar configuración
        assert compressor.config['enabled'] is True
        assert compressor.config['compression_level'] == "ebook"
        assert compressor.config['target_dpi'] == 200
        assert compressor.config['image_quality'] == 85
        assert compressor.config['remove_metadata'] is True
        assert compressor.config['fallback_on_error'] is True

        print("✅ PDFCompressor inicializado correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en test_pdf_compressor_init: {e}")
        return False

def test_pdf_compressor_tools_detection():
    """Test de detección de herramientas disponibles"""
    try:
        config = {"enabled": True}
        compressor = PDFCompressor(config)

        # Verificar que se detecten herramientas
        info = compressor.get_compression_info()

        print(f"📊 Herramientas detectadas:")
        print(f"   - Ghostscript: {info['tools_available']['ghostscript']}")
        print(f"   - pikepdf: {info['tools_available']['pikepdf']}")
        print(f"   - pypdf: {info['tools_available']['pypdf']}")

        # Al menos una herramienta debe estar disponible
        tools_available = any(info['tools_available'].values())
        assert tools_available, "No se detectaron herramientas de compresión"

        print("✅ Herramientas de compresión detectadas correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en test_pdf_compressor_tools_detection: {e}")
        return False

def test_pdf_compression_config_validation():
    """Test de validación de configuración"""
    try:
        # Test con configuración inválida
        invalid_config = {
            "enabled": True,
            "compression_level": "invalid_level",  # Nivel inválido
            "target_dpi": 200,
            "image_quality": 85
        }

        compressor = PDFCompressor(invalid_config)

        # Debe corregir automáticamente a "ebook"
        assert compressor.config['compression_level'] == "ebook"

        print("✅ Validación de configuración funciona correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en test_pdf_compression_config_validation: {e}")
        return False

def test_pdf_compressor_disabled():
    """Test cuando el compresor está deshabilitado"""
    try:
        config = {"enabled": False}
        compressor = PDFCompressor(config)

        # Crear archivos temporales
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as input_file:
            input_path = Path(input_file.name)
            input_file.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_file:
            output_path = Path(output_file.name)

        # Test con compresor deshabilitado
        result = compressor.compress(input_path, output_path)

        # Debe retornar True sin procesar
        assert result is True

        # Limpiar archivos temporales
        input_path.unlink()
        if output_path.exists():
            output_path.unlink()

        print("✅ Comportamiento con compresor deshabilitado correcto")
        return True

    except Exception as e:
        print(f"❌ Error en test_pdf_compressor_disabled: {e}")
        return False

def run_all_compression_tests():
    """Ejecuta todos los tests de compresión"""
    print("🧪 Iniciando tests de compresión de PDF...")
    print("=" * 50)

    tests = [
        test_pdf_compressor_init,
        test_pdf_compressor_tools_detection,
        test_pdf_compression_config_validation,
        test_pdf_compressor_disabled
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} falló con excepción: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"📊 Resumen de tests:")
    print(f"   ✅ Pasaron: {passed}")
    print(f"   ❌ Fallaron: {failed}")
    print(f"   📊 Total: {passed + failed}")

    return failed == 0

if __name__ == "__main__":
    import sys
    success = run_all_compression_tests()
    if success:
        print("🎉 Todos los tests de compresión pasaron!")
        sys.exit(0)
    else:
        print("💥 Algunos tests de compresión fallaron")
        sys.exit(1)
