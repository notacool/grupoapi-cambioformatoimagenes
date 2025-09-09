#!/usr/bin/env python3
"""
Script para monitorear el progreso de la conversión en tiempo real
"""

import os
import sys
import time
from pathlib import Path
from collections import defaultdict

def monitorear_progreso(directorio_raiz, intervalo=30):
    """
    Monitorea el progreso de la conversión cada X segundos
    """
    print("🔍 MONITOREO DE PROGRESO DE CONVERSIÓN")
    print("=" * 50)
    print(f"📁 Directorio: {directorio_raiz}")
    print(f"⏱️  Intervalo: {intervalo} segundos")
    print("Presiona Ctrl+C para detener el monitoreo")
    print()
    
    directorio = Path(directorio_raiz)
    if not directorio.exists():
        print(f"❌ Error: El directorio {directorio_raiz} no existe")
        return False
    
    try:
        while True:
            # Limpiar pantalla (funciona en Windows y Linux)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🔍 MONITOREO DE PROGRESO DE CONVERSIÓN")
            print("=" * 50)
            print(f"📁 Directorio: {directorio_raiz}")
            print(f"⏱️  Última actualización: {time.strftime('%H:%M:%S')}")
            print()
            
            # Estadísticas generales
            stats = {
                'subcarpetas_tiff': 0,
                'archivos_tiff': 0,
                'archivos_jpg_high': 0,
                'archivos_jpg_low': 0,
                'archivos_pdf': 0,
                'archivos_mets': 0,
                'pdf_consolidados': 0,
                'subcarpetas_procesadas': 0
            }
            
            # Buscar todas las subcarpetas con TIFF
            subcarpetas_tiff = []
            for item in directorio.iterdir():
                if item.is_dir():
                    tiff_folder = item / "TIFF"
                    if tiff_folder.exists() and tiff_folder.is_dir():
                        subcarpetas_tiff.append(item)
                        stats['subcarpetas_tiff'] += 1
            
            print(f"📁 Subcarpetas con TIFF: {stats['subcarpetas_tiff']}")
            
            # Verificar cada subcarpeta
            for subcarpeta in sorted(subcarpetas_tiff):
                # Contar archivos TIFF originales
                tiff_folder = subcarpeta / "TIFF"
                archivos_tiff = list(tiff_folder.glob("*.tif")) + list(tiff_folder.glob("*.tiff"))
                stats['archivos_tiff'] += len(archivos_tiff)
                
                # Verificar carpetas de salida
                carpetas_salida = ['JPGHIGH', 'JPGLOW', 'PDF', 'METS']
                subcarpeta_procesada = False
                
                for carpeta in carpetas_salida:
                    carpeta_path = subcarpeta / carpeta
                    if carpeta_path.exists():
                        if carpeta == 'JPGHIGH':
                            archivos = list(carpeta_path.glob("*.jpg"))
                            stats['archivos_jpg_high'] += len(archivos)
                        elif carpeta == 'JPGLOW':
                            archivos = list(carpeta_path.glob("*.jpg"))
                            stats['archivos_jpg_low'] += len(archivos)
                        elif carpeta == 'PDF':
                            archivos = list(carpeta_path.glob("*.pdf"))
                            stats['archivos_pdf'] += len(archivos)
                            
                            # Buscar PDFs consolidados
                            pdfs_consolidados = [f for f in archivos if 'consolidated' in f.name.lower() or f.name.startswith(subcarpeta.name)]
                            stats['pdf_consolidados'] += len(pdfs_consolidados)
                        elif carpeta == 'METS':
                            archivos = list(carpeta_path.glob("*.xml"))
                            stats['archivos_mets'] += len(archivos)
                        
                        subcarpeta_procesada = True
                
                if subcarpeta_procesada:
                    stats['subcarpetas_procesadas'] += 1
            
            # Mostrar resumen
            print(f"📁 Subcarpetas procesadas: {stats['subcarpetas_procesadas']}/{stats['subcarpetas_tiff']}")
            print(f"📄 Archivos TIFF originales: {stats['archivos_tiff']}")
            print(f"🖼️  Archivos JPG High: {stats['archivos_jpg_high']}")
            print(f"🖼️  Archivos JPG Low: {stats['archivos_jpg_low']}")
            print(f"📄 Archivos PDF: {stats['archivos_pdf']}")
            print(f"📚 PDFs consolidados: {stats['pdf_consolidados']}")
            print(f"📋 Archivos METS: {stats['archivos_mets']}")
            
            # Calcular porcentajes de conversión
            if stats['archivos_tiff'] > 0:
                print("\n📈 PORCENTAJES DE CONVERSIÓN")
                print("=" * 30)
                print(f"JPG High: {(stats['archivos_jpg_high'] / stats['archivos_tiff'] * 100):.1f}%")
                print(f"JPG Low: {(stats['archivos_jpg_low'] / stats['archivos_tiff'] * 100):.1f}%")
                print(f"PDF: {(stats['archivos_pdf'] / stats['archivos_tiff'] * 100):.1f}%")
            
            # Verificar si hay problemas
            problemas = []
            if stats['subcarpetas_procesadas'] == 0:
                problemas.append("❌ No se procesó ninguna subcarpeta")
            if stats['archivos_pdf'] == 0 and stats['archivos_jpg_high'] == 0:
                problemas.append("❌ No se generaron archivos")
            
            if problemas:
                print("\n⚠️  PROBLEMAS DETECTADOS:")
                for problema in problemas:
                    print(f"   {problema}")
            else:
                print("\n✅ ¡Conversión en progreso!")
            
            print(f"\n⏳ Próxima actualización en {intervalo} segundos...")
            time.sleep(intervalo)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoreo detenido por el usuario")
        return True

def main():
    if len(sys.argv) < 2:
        print("Uso: python monitorear_progreso.py <directorio_raiz> [intervalo_segundos]")
        print("Ejemplo: python monitorear_progreso.py \"D:\\alicante brutos\\GRANJA\" 30")
        sys.exit(1)
    
    directorio_raiz = sys.argv[1]
    intervalo = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    exito = monitorear_progreso(directorio_raiz, intervalo)
    sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()
