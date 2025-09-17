#!/usr/bin/env python3
"""
Test simple para verificar el Consolidated PDF Postconverter
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_consolidated_pdf():
    """Test simple del postconversor"""
    print("🧪 Probando Consolidated PDF Postconverter...")
    
    try:
        from src.postconverters.consolidated_pdf_postconverter import ConsolidatedPDFPostconverter
        
        # Configuración de prueba
        config = {
            "enabled": True,
            "max_size_mb": 10,
            "output_folder": "PDF",
            "use_ocr": True,
            "sort_by_name": True
        }
        
        # Crear instancia
        postconverter = ConsolidatedPDFPostconverter(config)
        print(f"✅ Postconversor creado: {postconverter.get_name()}")
        print(f"   📏 Tamaño máximo: {postconverter.max_size_mb} MB")
        print(f"   📁 Carpeta de salida: {postconverter.output_folder}")
        
        # Probar métodos internos
        test_files = [Path(f"test_{i:02d}.tiff") for i in range(10)]
        files_per_pdf = postconverter._calculate_files_per_pdf(test_files)
        print(f"   📋 Archivos por PDF: {files_per_pdf}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_imports():
    """Test de imports"""
    print("🧪 Probando imports...")
    
    try:
        from src.postconverters import ConsolidatedPDFPostconverter, METFormatPostConverter
        print("✅ Imports exitosos")
        return True
    except Exception as e:
        print(f"❌ Error en imports: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Test Simple del Conversor TIFF v2.0")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Consolidated PDF", test_consolidated_pdf)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASÓ")
        else:
            print(f"❌ {test_name} FALLÓ")
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron!")
    else:
        print("⚠️  Algunas pruebas fallaron")
