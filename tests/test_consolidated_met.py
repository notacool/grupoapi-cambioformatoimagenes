#!/usr/bin/env python3
"""
Script de prueba para el archivo MET consolidado
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.converters.met_metadata_converter import METMetadataConverter

def test_consolidated_met():
    """Prueba la generación del archivo MET consolidado"""
    
    # Configuración de prueba - Archivos con timestamp
    config_timestamp = {
        'include_image_metadata': True,
        'include_file_metadata': True,
        'include_processing_info': True,
        'metadata_standard': 'MET',
        'organization': 'Sistema de Pruebas',
        'creator': 'Script de Prueba',
        'generate_all_met': True  # Genera archivos con timestamp
    }
    
    # Configuración de prueba - Un archivo por formato
    config_single = {
        'include_image_metadata': True,
        'include_file_metadata': True,
        'include_processing_info': True,
        'metadata_standard': 'MET',
        'organization': 'Sistema de Pruebas',
        'creator': 'Script de Prueba',
        'generate_all_met': False  # Genera un archivo por formato
    }
    
    # Probar ambas configuraciones
    print("🧪 Probando configuración 1: Archivos con timestamp")
    met_converter_timestamp = METMetadataConverter(config_timestamp)
    
    print("🧪 Probando configuración 2: Un archivo por formato")
    met_converter_single = METMetadataConverter(config_single)
    
    # Datos de prueba simulando resultados de conversión
    conversion_results = [
        {
            'input_file': Path('test_input/documento1.tiff'),
            'output_files': [
                {
                    'format': 'jpg_400',
                    'path': Path('test_output/jpg_400/documento1_400.jpg'),
                    'size': 1024000
                },
                {
                    'format': 'pdf_easyocr',
                    'path': Path('test_output/pdf_easyocr/documento1_OCR.pdf'),
                    'size': 2048000
                }
            ],
            'success': True
        },
        {
            'input_file': Path('test_input/documento2.tiff'),
            'output_files': [
                {
                    'format': 'jpg_200',
                    'path': Path('test_output/jpg_200/documento2_200.jpg'),
                    'size': 512000
                },
                {
                    'format': 'met_metadata',
                    'path': Path('test_output/met_metadata/documento2_MET.xml'),
                    'size': 8192
                }
            ],
            'success': True
        }
    ]
    
    # Generar archivo consolidado
    output_path = Path('test_output/CONSOLIDATED_MET_TEST.xml')
    
    print("🧪 Probando generación de archivos MET por formato...")
    print(f"📁 Archivos de entrada: {len(conversion_results)}")
    print(f"📋 Formatos incluidos: {set()}")
    
    for result in conversion_results:
        for output_file in result['output_files']:
            print(f"   - {output_file['format']}: {output_file['path'].name}")
    
    # Probar configuración 1: Archivos con timestamp
    print("\n📋 CONFIGURACIÓN 1: Archivos con timestamp")
    results_timestamp = met_converter_timestamp.create_format_specific_met(conversion_results, output_path.parent)
    
    if results_timestamp:
        print(f"✅ Archivos MET con timestamp generados para {len(results_timestamp)} formatos")
        successful_formats = [fmt for fmt, success in results_timestamp.items() if success]
        if successful_formats:
            print(f"📋 Formatos exitosos: {', '.join(successful_formats)}")
            
            # Mostrar ejemplo de archivo con timestamp
            for format_type in successful_formats:
                met_files = list(output_path.parent.glob(f"MET_{format_type.upper()}_*.xml"))
                if met_files:
                    example_file = met_files[0]
                    print(f"📁 Archivo generado: {example_file.name}")
                    break
    else:
        print("❌ Error generando archivos MET con timestamp")
    
    # Probar configuración 2: Un archivo por formato
    print("\n📋 CONFIGURACIÓN 2: Un archivo por formato")
    results_single = met_converter_single.create_format_specific_met(conversion_results, output_path.parent)
    
    if results_single:
        print(f"✅ Archivos MET únicos generados para {len(results_single)} formatos")
        successful_formats = [fmt for fmt, success in results_single.items() if success]
        if successful_formats:
            print(f"📋 Formatos exitosos: {', '.join(successful_formats)}")
            
            # Mostrar ejemplo de archivo único
            for format_type in successful_formats:
                met_file = output_path.parent / f"{format_type}.xml"
                if met_file.exists():
                    print(f"📁 Archivo generado: {met_file.name}")
                    break
    else:
        print("❌ Error generando archivos MET únicos")
    
    # Retornar éxito si al menos una configuración funcionó
    return any(results_timestamp.values()) if results_timestamp else False or any(results_single.values()) if results_single else False

if __name__ == '__main__':
    print("🚀 PRUEBA DE ARCHIVOS MET POR FORMATO")
    print("=" * 50)
    
    try:
        success = test_consolidated_met()
        if success:
            print("\n🎉 ¡Prueba completada exitosamente!")
        else:
            print("\n💥 La prueba falló")
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
