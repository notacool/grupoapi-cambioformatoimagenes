#!/usr/bin/env python3
"""
Test simple para verificar la funcionalidad de procesamiento por subcarpeta
"""

import os
from pathlib import Path

def test_subfolder_structure():
    """Test básico de la estructura de subcarpetas"""
    print("🧪 TEST: Verificando estructura de subcarpetas")
    
    # Verificar que existe la estructura de entrada
    input_dir = Path("test_subfolder_input")
    if not input_dir.exists():
        print("❌ Error: No existe el directorio de entrada de prueba")
        return False
    
    # Verificar subcarpetas
    expected_subfolders = ["madraza", "valencia", "alicante", "barcelona"]
    for subfolder in expected_subfolders:
        subfolder_path = input_dir / subfolder
        if not subfolder_path.exists():
            print(f"❌ Error: No existe la subcarpeta {subfolder}")
            return False
    
    # Verificar carpetas TIFF
    tiff_subfolders = ["madraza", "valencia"]
    for subfolder in tiff_subfolders:
        tiff_path = input_dir / subfolder / "TIFF"
        if not tiff_path.exists():
            print(f"❌ Error: No existe la carpeta TIFF en {subfolder}")
            return False
        
        # Verificar archivos TIFF
        tiff_files = list(tiff_path.glob("*.tiff"))
        if len(tiff_files) != 3:
            print(f"❌ Error: Se esperaban 3 archivos TIFF en {subfolder}, se encontraron {len(tiff_files)}")
            return False
    
    print("✅ Estructura de entrada correcta")
    return True

def test_output_structure():
    """Test básico de la estructura de salida"""
    print("\n🧪 TEST: Verificando estructura de salida")
    
    # Verificar que existe la estructura de salida
    output_dir = Path("test_subfolder_output_full")
    if not output_dir.exists():
        print("❌ Error: No existe el directorio de salida de prueba")
        return False
    
    # Verificar subcarpetas de salida
    expected_output_subfolders = ["madraza", "valencia"]
    for subfolder in expected_output_subfolders:
        subfolder_path = output_dir / subfolder
        if not subfolder_path.exists():
            print(f"❌ Error: No existe la subcarpeta de salida {subfolder}")
            return False
        
        # Verificar formatos generados
        expected_formats = ["JPGHIGH", "JPGLOW", "PDF", "METS"]
        for format_name in expected_formats:
            format_path = subfolder_path / format_name
            if not format_path.exists():
                print(f"❌ Error: No existe el directorio de formato {format_name} en {subfolder}")
                return False
            
            # Verificar archivos generados
            if format_name in ["JPGHIGH", "JPGLOW"]:
                jpg_files = list(format_path.glob("*.jpg"))
                if len(jpg_files) != 3:
                    print(f"❌ Error: Se esperaban 3 archivos JPG en {subfolder}/{format_name}, se encontraron {len(jpg_files)}")
                    return False
            elif format_name == "PDF":
                pdf_files = list(format_path.glob("*.pdf"))
                if len(pdf_files) != 3:
                    print(f"❌ Error: Se esperaban 3 archivos PDF en {subfolder}/{format_name}, se encontraron {len(pdf_files)}")
                    return False
            elif format_name == "METS":
                xml_files = list(format_path.glob("*.xml"))
                if len(xml_files) != 1:
                    print(f"❌ Error: Se esperaba 1 archivo XML en {subfolder}/{format_name}, se encontraron {len(xml_files)}")
                    return False
    
    print("✅ Estructura de salida correcta")
    return True

def test_logs():
    """Test básico de los archivos de log"""
    print("\n🧪 TEST: Verificando archivos de log")
    
    logs_dir = Path("test_subfolder_output_full/logs")
    if not logs_dir.exists():
        print("❌ Error: No existe el directorio de logs")
        return False
    
    log_files = list(logs_dir.glob("*.log"))
    if len(log_files) == 0:
        print("❌ Error: No se encontraron archivos de log")
        return False
    
    print(f"✅ Se encontraron {len(log_files)} archivos de log")
    
    # Verificar contenido del log más reciente
    latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
    with open(latest_log, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Verificar que contiene información de ambas subcarpetas
        if "madraza" not in content or "valencia" not in content:
            print("❌ Error: El log no contiene información de ambas subcarpetas")
            return False
        
        # Verificar que contiene información de conversiones
        if "Conversiones exitosas" not in content:
            print("❌ Error: El log no contiene información de conversiones")
            return False
    
    print("✅ Contenido del log correcto")
    return True

def main():
    """Función principal de testing"""
    print("🚀 INICIANDO TESTS DE FUNCIONALIDAD DE SUBCARPETAS")
    print("=" * 60)
    
    tests = [
        test_subfolder_structure,
        test_output_structure,
        test_logs
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error ejecutando test: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DE LOS TESTS")
    print("=" * 60)
    print(f"✅ Tests exitosos: {passed}/{total}")
    print(f"❌ Tests fallidos: {total - passed}")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests han pasado exitosamente!")
        print("✅ La funcionalidad de procesamiento por subcarpeta está funcionando correctamente")
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron")
        print("🔧 Revisa los errores arriba para identificar problemas")
    
    return passed == total

if __name__ == "__main__":
    main()
