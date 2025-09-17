#!/usr/bin/env python3
"""
Script de prueba para el conversor MET Metadata
Genera archivos XML MET con metadatos detallados de archivos TIFF
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.converters.met_metadata_converter import METMetadataConverter


def test_met_converter():
    """Prueba el conversor MET con un archivo de ejemplo"""
    
    print("🧪 PRUEBA DEL CONVERSOR MET METADATA")
    print("=" * 50)
    
    # Configuración del conversor
    config = {
        'include_image_metadata': True,
        'include_file_metadata': True,
        'include_processing_info': True,
        'metadata_standard': 'MET',
        'organization': 'Sistema de Pruebas',
        'creator': 'Conversor TIFF v2.0'
    }
    
    try:
        # Crear instancia del conversor
        converter = METMetadataConverter(config)
        print("✅ Conversor MET inicializado correctamente")
        
        # Mostrar información del conversor
        info = converter.get_converter_info()
        print(f"\n📋 Información del conversor:")
        print(f"   Clase: {info['class']}")
        print(f"   Formato: {info['format']}")
        print(f"   Extensión: {info['extension']}")
        print(f"   Estándar: {info['metadata_standard']}")
        print(f"   Organización: {info['organization']}")
        print(f"   Creador: {info['creator']}")
        
        # Verificar archivos TIFF disponibles para prueba
        test_dir = Path("test_input")
        if not test_dir.exists():
            print(f"\n⚠️  Directorio de prueba no encontrado: {test_dir}")
            print("   Crea el directorio 'test_input' y coloca archivos TIFF para probar")
            return False
        
        tiff_files = list(test_dir.glob("*.tif*"))
        if not tiff_files:
            print(f"\n⚠️  No se encontraron archivos TIFF en: {test_dir}")
            print("   Coloca archivos .tiff o .tif en el directorio 'test_input'")
            return False
        
        print(f"\n📁 Archivos TIFF encontrados: {len(tiff_files)}")
        for tiff_file in tiff_files:
            print(f"   - {tiff_file.name}")
        
        # Crear directorio de salida
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Procesar cada archivo TIFF
        print(f"\n🔄 Procesando archivos...")
        for tiff_file in tiff_files:
            print(f"\n📄 Procesando: {tiff_file.name}")
            
            # Generar ruta de salida
            output_path = converter.get_output_filename(tiff_file, output_dir)
            print(f"   Salida: {output_path.name}")
            
            # Convertir archivo
            success = converter.convert(tiff_file, output_path)
            if success:
                print(f"   ✅ Metadatos MET generados exitosamente")
                
                # Mostrar información del archivo generado
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    print(f"   📊 Tamaño del archivo MET: {file_size} bytes")
                    
                    # Leer y mostrar parte del contenido XML
                    try:
                        with open(output_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')
                            print(f"   📋 Primeras líneas del XML:")
                            for i, line in enumerate(lines[:5]):
                                if line.strip():
                                    print(f"      {i+1}: {line.strip()}")
                            if len(lines) > 5:
                                print(f"      ... ({len(lines)} líneas total)")
                    except Exception as e:
                        print(f"   ⚠️  No se pudo leer el contenido: {e}")
            else:
                print(f"   ❌ Error generando metadatos MET")
        
        print(f"\n🎯 Prueba completada")
        print(f"📂 Archivos MET generados en: {output_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_usage():
    """Muestra información de uso del conversor MET"""
    
    print("\n📖 INFORMACIÓN DEL CONVERSOR MET")
    print("=" * 40)
    
    print("\n🎯 Propósito:")
    print("   Genera archivos XML MET (Metadata Encoding and Transmission Standard)")
    print("   con metadatos detallados de archivos TIFF")
    
    print("\n📋 Metadatos incluidos:")
    print("   • Información técnica de la imagen (dimensiones, DPI, formato)")
    print("   • Metadatos del archivo (tamaño, fechas, permisos)")
    print("   • Información de procesamiento (conversor, configuración)")
    print("   • Checksum MD5 para verificación de integridad")
    print("   • Metadatos EXIF si están disponibles")
    
    print("\n🔧 Configuración disponible:")
    print("   • include_image_metadata: Incluir metadatos de imagen")
    print("   • include_file_metadata: Incluir metadatos del archivo")
    print("   • include_processing_info: Incluir información de procesamiento")
    print("   • metadata_standard: Estándar de metadatos (MET)")
    print("   • organization: Nombre de la organización")
    print("   • creator: Nombre del sistema creador")
    
    print("\n📁 Estructura de salida:")
    print("   • Directorio: met_metadata/")
    print("   • Formato: {nombre_original}_MET.xml")
    print("   • Estándar: METS (Library of Congress)")
    
    print("\n💡 Casos de uso:")
    print("   • Archivos de preservación digital")
    print("   • Catálogos de bibliotecas y archivos")
    print("   • Sistemas de gestión documental")
    print("   • Cumplimiento de estándares de metadatos")


if __name__ == "__main__":
    print("🔧 CONVERSOR TIFF - GENERADOR DE METADATOS MET")
    print("=" * 60)
    
    # Mostrar información de uso
    show_usage()
    
    # Ejecutar prueba
    print("\n" + "=" * 60)
    success = test_met_converter()
    
    if success:
        print("\n✅ Prueba completada exitosamente")
        print("📋 Revisa los archivos XML generados en el directorio 'test_output'")
    else:
        print("\n❌ La prueba no se pudo completar")
        print("🔍 Revisa los mensajes de error anteriores")
    
    print("\n💡 Para usar en producción:")
    print("   python main.py --input 'entrada' --output 'salida' --formats met_metadata")
