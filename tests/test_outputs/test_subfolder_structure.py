#!/usr/bin/env python3
"""
Script de prueba para demostrar la nueva funcionalidad de procesamiento por subcarpeta
"""

import os
from pathlib import Path

def create_test_structure():
    """Crea una estructura de prueba para demostrar el procesamiento por subcarpeta"""
    
    # Crear directorio raíz de prueba
    test_root = Path("test_subfolder_input")
    test_root.mkdir(exist_ok=True)
    
    # Crear subcarpetas con diferentes estructuras
    subfolders = [
        "alicante",      # Sin carpeta TIFF - no se procesará
        "madraza",       # Con carpeta TIFF - se procesará
        "valencia",      # Con carpeta TIFF - se procesará
        "barcelona"      # Sin carpeta TIFF - no se procesará
    ]
    
    for subfolder in subfolders:
        subfolder_path = test_root / subfolder
        subfolder_path.mkdir(exist_ok=True)
        
        # Solo algunas subcarpetas tendrán carpetas TIFF
        if subfolder in ["madraza", "valencia"]:
            tiff_folder = subfolder_path / "TIFF"
            tiff_folder.mkdir(exist_ok=True)
            
            # Crear archivos TIFF de ejemplo (simulados)
            for i in range(1, 4):  # 3 archivos por carpeta
                tiff_file = tiff_folder / f"documento_{subfolder}_{i}.tiff"
                tiff_file.write_text(f"Simulación de archivo TIFF {i} de {subfolder}")
                print(f"✅ Creado: {tiff_file}")
        else:
            # Crear archivo de texto para indicar que no tiene TIFF
            info_file = subfolder_path / "INFO.txt"
            info_file.write_text(f"Esta subcarpeta no contiene carpeta TIFF y no será procesada")
            print(f"ℹ️  Creado: {info_file}")
    
    print(f"\n📁 Estructura de prueba creada en: {test_root.absolute()}")
    print("📋 Subcarpetas que se procesarán: madraza, valencia")
    print("📋 Subcarpetas que NO se procesarán: alicante, barcelona")
    
    return test_root

def show_usage_example():
    """Muestra ejemplos de uso del nuevo sistema"""
    
    print("\n" + "="*60)
    print("🚀 EJEMPLOS DE USO DEL NUEVO SISTEMA")
    print("="*60)
    
    print("\n1️⃣  Conversión básica por subcarpeta:")
    print("   python main.py --input test_subfolder_input --output test_subfolder_output")
    
    print("\n2️⃣  Conversión con formatos específicos:")
    print("   python main.py --input test_subfolder_input --output test_subfolder_output --formats JPGHIGH,PDF")
    
    print("\n3️⃣  Conversión con modo verbose:")
    print("   python main.py --input test_subfolder_input --output test_subfolder_output --verbose")
    
    print("\n4️⃣  Conversión solo de metadatos MET:")
    print("   python main.py --input test_subfolder_input --output test_subfolder_output --formats METS")
    
    print("\n" + "="*60)
    print("📁 ESTRUCTURA DE SALIDA ESPERADA:")
    print("="*60)
    
    print("""
test_subfolder_output/
├── logs/                                    # Archivos de log
│   ├── conversion_madraza_YYYYMMDD_HHMMSS.log
│   └── conversion_valencia_YYYYMMDD_HHMMSS.log
├── madraza/                                 # Subcarpeta procesada
│   ├── METS/
│   │   └── madraza_TIFF.xml               # METS del TIFF original
│   ├── JPGHIGH/
│   │   ├── documento_madraza_1.jpg
│   │   ├── documento_madraza_2.jpg
│   │   ├── documento_madraza_3.jpg
│   │   └── JPGHIGH.xml                    # Metadatos consolidados
│   ├── JPGLOW/
│   │   ├── documento_madraza_1.jpg
│   │   ├── documento_madraza_2.jpg
│   │   ├── documento_madraza_3.jpg
│   │   └── JPGLOW.xml                     # Metadatos consolidados
│   └── PDF/
│       ├── documento_madraza_1_EasyOCR.pdf
│       ├── documento_madraza_2_EasyOCR.pdf
│       ├── documento_madraza_3_EasyOCR.pdf
│       └── PDF.xml                         # Metadatos consolidados
└── valencia/                                # Subcarpeta procesada
    ├── METS/
    │   └── valencia_TIFF.xml              # METS del TIFF original
    ├── JPGHIGH/
    │   ├── documento_valencia_1.jpg
    │   ├── documento_valencia_2.jpg
    │   ├── documento_valencia_3.jpg
    │   └── JPGHIGH.xml                    # Metadatos consolidados
    ├── JPGLOW/
    │   ├── documento_valencia_1.jpg
    │   ├── documento_valencia_2.jpg
    │   ├── documento_valencia_3.jpg
    │   └── JPGLOW.xml                     # Metadatos consolidados
    └── PDF/
        ├── documento_valencia_1_EasyOCR.pdf
        ├── documento_valencia_2_EasyOCR.pdf
        ├── documento_valencia_3_EasyOCR.pdf
        └── PDF.xml                         # Metadatos consolidados
    """)

def main():
    """Función principal"""
    
    print("🧪 CREANDO ESTRUCTURA DE PRUEBA PARA PROCESAMIENTO POR SUBCARPETA")
    print("="*70)
    
    # Crear estructura de prueba
    test_root = create_test_structure()
    
    # Mostrar ejemplos de uso
    show_usage_example()
    
    print(f"\n🎯 Para probar el sistema:")
    print(f"   1. Ejecuta: python main.py --input {test_root} --output test_subfolder_output")
    print(f"   2. Revisa la carpeta de salida para ver la estructura generada")
    print(f"   3. Revisa la carpeta 'logs' para ver los archivos de log")
    
    print(f"\n📋 Notas importantes:")
    print(f"   - Solo las subcarpetas con carpetas 'TIFF' serán procesadas")
    print(f"   - Cada subcarpeta generará su propia estructura de salida")
    print(f"   - Los archivos MET se generarán por subcarpeta")
    print(f"   - Los logs se guardarán automáticamente")

if __name__ == "__main__":
    main()
