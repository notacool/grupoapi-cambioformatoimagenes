#!/usr/bin/env python3
"""
Script de prueba para verificar el corrector de nombres de subcarpetas.
"""

import tempfile
import shutil
from pathlib import Path
from corregir_nombres_subcarpetas import CorrectorNombresSubcarpetas


def crear_estructura_prueba():
    """Crea una estructura de prueba para testear el corrector"""
    
    # Crear directorio temporal
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 Directorio temporal: {temp_dir}")
    
    # Estructura de entrada (correcta)
    input_dir = temp_dir / "input"
    input_dir.mkdir()
    
    # Crear algunas carpetas TIFF anidadas
    carpetas_tiff = [
        "231/231_4/231_4/TIFF",
        "232/232_1/232_1_1/TIFF", 
        "233/233_2/TIFF",
        "234/TIFF"  # Esta no es anidada
    ]
    
    for carpeta in carpetas_tiff:
        carpeta_path = input_dir / carpeta
        carpeta_path.mkdir(parents=True)
        # Crear algunos archivos TIFF ficticios
        for i in range(3):
            (carpeta_path / f"imagen_{i:03d}.tiff").touch()
    
    # Estructura de salida (con nombres incorrectos)
    output_dir = temp_dir / "output"
    output_dir.mkdir()
    
    # Crear carpetas con nombres incorrectos (simulando el problema)
    carpetas_incorrectas = [
        "231_231_4_231_4",  # Debería ser "231/231_4/231_4"
        "232_232_1_232_1_1",  # Debería ser "232/232_1/232_1_1"
        "233_233_2",  # Debería ser "233/233_2"
        "234"  # Esta está correcta
    ]
    
    # Crear también algunas carpetas con nombres correctos (conversión anterior)
    carpetas_correctas = [
        "231/231_4/231_4",  # Conversión anterior
        "232/232_1/232_1_1",  # Conversión anterior
    ]
    
    # Crear carpetas con nombres incorrectos (conversión actual)
    for carpeta in carpetas_incorrectas:
        carpeta_path = output_dir / carpeta
        carpeta_path.mkdir()
        
        # Crear subcarpetas de formatos
        for formato in ["JPGHIGH", "JPGLOW", "PDF", "METS"]:
            (carpeta_path / formato).mkdir()
            
        # Crear algunos archivos de ejemplo
        for formato in ["JPGHIGH", "JPGLOW", "PDF"]:
            for i in range(3):
                extension = ".jpg" if "JPG" in formato else ".pdf"
                (carpeta_path / formato / f"imagen_{i:03d}{extension}").touch()
    
    # Crear carpetas con nombres correctos (conversión anterior)
    for carpeta in carpetas_correctas:
        carpeta_path = output_dir / carpeta
        carpeta_path.mkdir(parents=True)
        
        # Crear subcarpetas de formatos
        for formato in ["JPGHIGH", "JPGLOW", "PDF", "METS"]:
            (carpeta_path / formato).mkdir()
            
        # Crear algunos archivos de ejemplo (conversión anterior)
        for formato in ["JPGHIGH", "JPGLOW", "PDF"]:
            for i in range(2):  # Menos archivos para simular conversión anterior
                extension = ".jpg" if "JPG" in formato else ".pdf"
                (carpeta_path / formato / f"anterior_{i:03d}{extension}").touch()
    
    # Crear algunos archivos METS con referencias incorrectas
    mets_dir = output_dir / "231_231_4_231_4" / "METS"
    mets_file = mets_dir / "231_231_4_231_4.xml"
    mets_file.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<root>\n    <path>231_231_4_231_4/JPGHIGH/imagen_001.jpg</path>\n    <reference>231_231_4_231_4/PDF/imagen_001.pdf</reference>\n</root>')
    
    return str(input_dir), str(output_dir)


def test_corrector():
    """Prueba el corrector de nombres"""
    
    print("🧪 Iniciando prueba del corrector de nombres...")
    
    # Crear estructura de prueba
    input_dir, output_dir = crear_estructura_prueba()
    
    try:
        # Crear corrector
        corrector = CorrectorNombresSubcarpetas(input_dir, output_dir)
        
        # Analizar problema
        print("\n1. Analizando problema...")
        tiff_folders = corrector.analizar_problema()
        
        # Generar plan de corrección
        print("\n2. Generando plan de corrección...")
        acciones = corrector.generar_plan_correccion(tiff_folders)
        
        # Mostrar plan
        print("\n📋 Plan de corrección:")
        for i, accion in enumerate(acciones, 1):
            print(f"   {i}. {accion['descripcion']}")
        
        # Ejecutar simulación
        print("\n3. Ejecutando simulación...")
        exito = corrector.ejecutar_correccion(acciones, dry_run=True)
        
        # Actualizar archivos METS (simulación)
        print("\n4. Actualizando archivos METS (simulación)...")
        exito_mets = corrector.actualizar_archivos_mets(dry_run=True)
        
        # Generar reporte
        print("\n5. Generando reporte...")
        corrector.generar_reporte(tiff_folders, acciones)
        
        if exito and exito_mets:
            print("\n✅ Prueba completada exitosamente")
            return True
        else:
            print("\n❌ Prueba completada con errores")
            return False
            
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        return False
    
    finally:
        # Limpiar directorio temporal
        try:
            shutil.rmtree(Path(input_dir).parent)
            print(f"\n🧹 Directorio temporal limpiado")
        except Exception as e:
            print(f"\n⚠️ Error limpiando directorio temporal: {str(e)}")


if __name__ == "__main__":
    success = test_corrector()
    exit(0 if success else 1)
