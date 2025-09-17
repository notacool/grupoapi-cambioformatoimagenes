#!/usr/bin/env python3
"""
Test específico para la funcionalidad de compresión de PDF
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.converters.pdf_easyocr_converter import PDFEasyOCRConverter
from src.converters.pdf_compressor import PDFCompressor


def test_pdf_converter_with_compression():
    """Prueba el conversor PDF con diferentes configuraciones de compresión"""

    print("🧪 PRUEBA DEL CONVERSOR PDF CON COMPRESIÓN")
    print("=" * 60)

    # Configuraciones de prueba
    configs = [
        {
            "name": "Sin compresión",
            "config": {
                "ocr_language": ["es"],
                "create_searchable_pdf": True,
                "use_gpu": False,
                "compression": {
                    "enabled": False
                }
            }
        },
        {
            "name": "Compresión básica",
            "config": {
                "ocr_language": ["es"],
                "create_searchable_pdf": True,
                "use_gpu": False,
                "compression": {
                    "enabled": True,
                    "compression_level": "ebook",
                    "target_dpi": 200,
                    "image_quality": 85,
                    "remove_metadata": True,
                    "fallback_on_error": True
                }
            }
        },
        {
            "name": "Compresión alta",
            "config": {
                "ocr_language": ["es"],
                "create_searchable_pdf": True,
                "use_gpu": False,
                "compression": {
                    "enabled": True,
                    "compression_level": "screen",
                    "target_dpi": 150,
                    "image_quality": 75,
                    "remove_metadata": True,
                    "fallback_on_error": True
                }
            }
        },
        {
            "name": "Compresión máxima calidad",
            "config": {
                "ocr_language": ["es"],
                "create_searchable_pdf": True,
                "use_gpu": False,
                "compression": {
                    "enabled": True,
                    "compression_level": "prepress",
                    "target_dpi": 300,
                    "image_quality": 95,
                    "remove_metadata": False,
                    "fallback_on_error": True
                }
            }
        }
    ]

    try:
        for config_info in configs:
            print(f"\n📋 Configuración: {config_info['name']}")
            print("-" * 40)

            # Crear instancia del conversor
            converter = PDFEasyOCRConverter(config_info['config'])

            # Mostrar información de compresión
            compression_enabled = config_info['config']['compression']['enabled']
            print(f"   🔧 Compresión habilitada: {compression_enabled}")

            if compression_enabled:
                comp_config = config_info['config']['compression']
                print(f"   📊 Nivel de compresión: {comp_config['compression_level']}")
                print(f"   🎯 DPI objetivo: {comp_config['target_dpi']}")
                print(f"   🖼️  Calidad de imagen: {comp_config['image_quality']}%")
                print(f"   🗑️  Eliminar metadatos: {comp_config['remove_metadata']}")
                print(f"   ⚠️  Fallback en error: {comp_config['fallback_on_error']}")

            # Verificar configuración del compresor
            if hasattr(converter, 'pdf_compressor'):
                compressor_info = converter.pdf_compressor.get_compression_info()
                print(f"   🛠️  Herramientas disponibles:")
                for tool, available in compressor_info['tools_available'].items():
                    status = "✅" if available else "❌"
                    print(f"      {status} {tool}")

            print(f"   ✅ Conversor inicializado correctamente")

        print(f"\n🎯 Todas las configuraciones probadas exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_compression_parameter_inheritance():
    """Prueba la herencia de parámetros de compresión en el conversor PDF"""

    print("\n🧪 PRUEBA DE HERENCIA DE PARÁMETROS")
    print("=" * 50)

    try:
        # Configuración con parámetros mixtos
        config = {
            "resolution": 300,  # Parámetro legacy del conversor
            "ocr_language": ["es"],
            "create_searchable_pdf": True,
            "use_gpu": False,
            "compression": {
                "enabled": True,
                "target_dpi": 150,  # Debe sobrescribir resolution
                "image_quality": 80,
                "compression_level": "ebook"
            }
        }

        converter = PDFEasyOCRConverter(config)

        # Verificar que los parámetros se heredaron correctamente
        print(f"📊 Verificando herencia de parámetros:")
        print(f"   🎯 DPI embebido: {converter.embed_target_dpi}")
        print(f"   🖼️  Calidad embebida: {converter.embed_image_quality}")

        # El DPI embebido debe ser el de compression, no el de resolution
        assert converter.embed_target_dpi == 150, f"DPI incorrecto: {converter.embed_target_dpi}"
        assert converter.embed_image_quality == 80, f"Calidad incorrecta: {converter.embed_image_quality}"

        print(f"   ✅ Parámetros heredados correctamente")

        # Prueba sin configuración de compression
        config_no_compression = {
            "resolution": 300,
            "ocr_language": ["es"],
            "create_searchable_pdf": True,
            "use_gpu": False
        }

        converter_no_comp = PDFEasyOCRConverter(config_no_compression)

        # Debe usar valores por defecto
        print(f"📊 Sin configuración de compresión:")
        print(f"   🎯 DPI embebido: {converter_no_comp.embed_target_dpi}")
        print(f"   🖼️  Calidad embebida: {converter_no_comp.embed_image_quality}")

        assert converter_no_comp.embed_target_dpi == 300, f"DPI por defecto incorrecto"
        assert converter_no_comp.embed_image_quality == 85, f"Calidad por defecto incorrecta"

        print(f"   ✅ Valores por defecto correctos")
        return True

    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_compression_usage():
    """Muestra información de uso de la compresión"""

    print("\n📖 INFORMACIÓN DE COMPRESIÓN DE PDF")
    print("=" * 50)

    print("\n🎯 Métodos de compresión disponibles:")
    print("   1. 📊 Compresión embebida (100% Python):")
    print("      • Calidad de imagen JPEG configurable")
    print("      • DPI objetivo para reducir tamaño del PDF")
    print("      • Optimización automática de JPEG")
    print("   2. 🔧 Post-compresión con herramientas:")
    print("      • pikepdf: Compresión de streams y metadatos")
    print("      • pypdf: Compresión básica")
    print("      • Ghostscript: Mejor compresión (opcional)")

    print("\n📋 Configuración recomendada:")
    print("   compression:")
    print("     enabled: true")
    print("     compression_level: 'ebook'        # screen|ebook|printer|prepress")
    print("     target_dpi: 200                   # DPI objetivo (150-300)")
    print("     image_quality: 85                 # Calidad JPEG (70-95)")
    print("     remove_metadata: true             # Eliminar metadatos")
    print("     fallback_on_error: true           # Usar original si falla")

    print("\n💡 Niveles de compresión:")
    print("   • screen:    Máxima compresión (72 DPI, web)")
    print("   • ebook:     Balanceado (150 DPI, lectura)")
    print("   • printer:   Buena calidad (300 DPI, impresión)")
    print("   • prepress:  Máxima calidad (300+ DPI, profesional)")

    print("\n🎯 Reducción esperada de tamaño:")
    print("   • Embebida:      20-50% (según DPI y calidad)")
    print("   • Post-compresión: 10-30% adicional")
    print("   • Total:         30-70% de reducción")


def run_all_pdf_compression_tests():
    """Ejecuta todos los tests de compresión de PDF"""
    print("🧪 INICIANDO TESTS DE COMPRESIÓN DE PDF")
    print("=" * 60)

    # Mostrar información de uso
    show_compression_usage()

    tests = [
        test_pdf_converter_with_compression,
        test_compression_parameter_inheritance
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

    print("=" * 60)
    print(f"📊 Resumen de tests:")
    print(f"   ✅ Pasaron: {passed}")
    print(f"   ❌ Fallaron: {failed}")
    print(f"   📊 Total: {passed + failed}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_pdf_compression_tests()
    if success:
        print("🎉 Todos los tests de compresión de PDF pasaron!")
        sys.exit(0)
    else:
        print("💥 Algunos tests de compresión de PDF fallaron")
        sys.exit(1)
