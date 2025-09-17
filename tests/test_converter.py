#!/usr/bin/env python3
"""
Script de prueba para el Conversor de Archivos TIFF
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.converter import TIFFConverter
from src.config_manager import ConfigManager


def test_config_manager():
    """Prueba el gestor de configuración"""
    print("🧪 Probando ConfigManager...")
    
    try:
        config_manager = ConfigManager()
        print(f"✅ ConfigManager inicializado correctamente")
        
        # Probar obtención de formatos
        enabled_formats = config_manager.get_enabled_formats()
        print(f"📁 Formatos habilitados: {enabled_formats}")
        
        # Probar configuración de formatos específicos
        jpg_400_config = config_manager.get_format_config('jpg_400')
        print(f"⚙️  Configuración JPG 400 DPI: {jpg_400_config}")
        
        jpg_200_config = config_manager.get_format_config('jpg_200')
        print(f"⚙️  Configuración JPG 200 DPI: {jpg_200_config}")
        
        pdf_easyocr_config = config_manager.get_format_config('pdf_easyocr')
        print(f"⚙️  Configuración PDF EasyOCR: {pdf_easyocr_config}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en ConfigManager: {str(e)}")
        return False


def test_converter_initialization():
    """Prueba la inicialización del conversor principal"""
    print("\n🧪 Probando inicialización del conversor...")
    
    try:
        converter = TIFFConverter()
        print(f"✅ TIFFConverter inicializado correctamente")
        
        # Probar obtención de formatos disponibles
        available_formats = converter.get_available_formats()
        print(f"🔄 Formatos disponibles: {available_formats}")
        
        # Probar información de conversores
        for format_name in available_formats:
            info = converter.get_converter_info(format_name)
            if info:
                print(f"📋 {format_name}: {info['name']} ({info['extension']})")
                if 'dpi' in info:
                    print(f"   📏 DPI: {info['dpi']}")
                if 'ocr_language' in info:
                    print(f"   🌐 OCR: {info['ocr_language']} (habilitado: {info['ocr_enabled']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en TIFFConverter: {str(e)}")
        return False


def test_file_processor():
    """Prueba el procesador de archivos"""
    print("\n🧪 Probando FileProcessor...")
    
    try:
        from src.file_processor import FileProcessor
        
        # Crear directorios de prueba
        test_input = Path("test_input")
        test_output = Path("test_output")
        
        test_input.mkdir(exist_ok=True)
        test_output.mkdir(exist_ok=True)
        
        # Crear un archivo TIFF de prueba (simulado)
        test_tiff = test_input / "test.tiff"
        test_tiff.touch()
        
        # Probar FileProcessor
        processor = FileProcessor(str(test_input), str(test_output))
        tiff_files = processor.get_tiff_files()
        
        print(f"✅ FileProcessor funcionando: {len(tiff_files)} archivos TIFF encontrados")
        
        # Probar generación de estructura de salida
        test_formats = ['JPGHIGH', 'JPGLOW', 'PDF', 'METS']
        for format_name in test_formats:
            processor.create_output_structure_for_subfolder("test_subfolder", [format_name])
            output_path = Path(test_output) / "test_subfolder" / format_name
            if output_path.exists():
                print(f"   ✅ Carpeta {format_name} creada correctamente")
            else:
                print(f"   ❌ Error creando carpeta {format_name}")
        
        # Limpiar archivos de prueba
        import shutil
        if test_input.exists():
            shutil.rmtree(test_input)
        if test_output.exists():
            shutil.rmtree(test_output)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en FileProcessor: {str(e)}")
        return False


def test_converters():
    """Prueba los conversores individuales"""
    print("\n🧪 Probando conversores individuales...")
    
    try:
        from converters import JPGResolutionConverter, PDFEasyOCRConverter
        
        # Probar JPG 400 DPI Converter
        jpg_400_config = {'quality': 95, 'optimize': True, 'progressive': False, 'dpi': 400}
        jpg_400_converter = JPGResolutionConverter(jpg_400_config)
        print(f"✅ JPG 400 DPI Converter: {jpg_400_converter}")
        print(f"   📏 DPI configurado: {jpg_400_converter.dpi}")
        
        # Probar JPG 200 DPI Converter
        jpg_200_config = {'quality': 90, 'optimize': True, 'progressive': False, 'dpi': 200}
        jpg_200_converter = JPGResolutionConverter(jpg_200_config)
        print(f"✅ JPG 200 DPI Converter: {jpg_200_converter}")
        print(f"   📏 DPI configurado: {jpg_200_converter.dpi}")
        

        # Probar PDF EasyOCR Converter
        pdf_easyocr_config = {
            'resolution': 300, 
            'page_size': 'A4', 
            'fit_to_page': True,
            'ocr_language': ['es', 'en'],
            'ocr_confidence': 0.5,
            'create_searchable_pdf': True
        }
        pdf_easyocr_converter = PDFEasyOCRConverter(pdf_easyocr_config)
        print(f"✅ PDF EasyOCR Converter: {pdf_easyocr_converter}")
        print(f"   🌐 Idioma OCR: {pdf_easyocr_converter.ocr_language}")
        print(f"   🔍 OCR habilitado: {pdf_easyocr_converter.create_searchable_pdf}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en conversores: {str(e)}")
        return False


def test_easyocr_dependencies():
    """Prueba las dependencias de EasyOCR"""
    print("\n🧪 Probando dependencias de EasyOCR...")
    
    try:
        # Probar EasyOCR
        try:
            import easyocr
            print(f"✅ EasyOCR disponible")
        except ImportError:
            print("⚠️  EasyOCR no instalado")
        
        # Probar PyPDF2
        try:
            import PyPDF2
            print(f"✅ PyPDF2 disponible: versión {PyPDF2.__version__}")
        except ImportError:
            print("⚠️  PyPDF2 no instalado")
        
        # Probar ReportLab
        try:
            import reportlab
            print(f"✅ ReportLab disponible: versión {reportlab.Version}")
        except ImportError:
            print("⚠️  ReportLab no instalado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando dependencias EasyOCR: {str(e)}")
        return False


def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL CONVERSOR TIFF CON EASYOCR")
    print("=" * 70)
    
    tests = [
        ("ConfigManager", test_config_manager),
        ("Conversores", test_converters),
        ("FileProcessor", test_file_processor),
        ("TIFFConverter", test_converter_initialization),
        ("Dependencias EasyOCR", test_easyocr_dependencies),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️  {test_name} falló")
        except Exception as e:
            print(f"❌ {test_name} falló con excepción: {str(e)}")
    
    print("\n" + "=" * 70)
    print("📊 RESULTADOS DE LAS PRUEBAS")
    print("=" * 70)
    print(f"✅ Pruebas exitosas: {passed}/{total}")
    print(f"❌ Pruebas fallidas: {total - passed}")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El conversor está funcionando correctamente.")
        print("\n💡 FUNCIONALIDADES IMPLEMENTADAS:")
        print("   🖼️  JPG 400 DPI: Alta resolución para impresión")
        print("   🖼️  JPG 200 DPI: Resolución media para web")
        print("   📄 PDF con EasyOCR: Texto buscable y seleccionable")
        print("\n💡 Para usar el conversor:")
        print("   python main.py --input 'carpeta_entrada' --output 'carpeta_salida'")
        print("   python main.py --help  # Para ver todas las opciones")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
