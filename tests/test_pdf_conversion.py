#!/usr/bin/env python3
"""
Script de prueba para diagnosticar el problema de conversión PDF
"""

import sys
from pathlib import Path
from PIL import Image
import tempfile
import time

def test_tiff_to_jpeg_conversion(tiff_path):
    """Prueba la conversión de TIFF a JPEG paso a paso"""
    print(f"🔍 Probando conversión: {tiff_path}")
    
    try:
        # Paso 1: Abrir imagen
        print("🔄 Paso 1: Abriendo imagen TIFF...")
        start_time = time.time()
        
        with Image.open(tiff_path) as pil_img:
            print(f"✅ Imagen abierta: {pil_img.size[0]}x{pil_img.size[1]} px, modo: {pil_img.mode}")
            print(f"⏱️ Tiempo apertura: {time.time() - start_time:.2f} segundos")
            
            # Paso 2: Convertir a RGB si es necesario
            print("🔄 Paso 2: Convirtiendo a RGB...")
            start_time = time.time()
            
            if pil_img.mode not in ["RGB", "L"]:
                pil_img = pil_img.convert("RGB")
                print(f"✅ Conversión completada")
            else:
                print(f"✅ Ya está en modo {pil_img.mode}")
            
            print(f"⏱️ Tiempo conversión: {time.time() - start_time:.2f} segundos")
            
            # Paso 3: Crear archivo temporal
            print("🔄 Paso 3: Creando archivo temporal...")
            start_time = time.time()
            
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                print(f"✅ Archivo temporal creado: {temp_path}")
                print(f"⏱️ Tiempo creación: {time.time() - start_time:.2f} segundos")
                
                # Paso 4: Guardar como JPEG
                print("🔄 Paso 4: Guardando como JPEG...")
                start_time = time.time()
                
                pil_img.save(
                    temp_path,
                    format="JPEG",
                    quality=85,
                    optimize=True,
                )
                
                print(f"✅ JPEG guardado exitosamente")
                print(f"⏱️ Tiempo guardado: {time.time() - start_time:.2f} segundos")
                
                # Verificar tamaño del archivo
                jpeg_size = temp_path.stat().st_size / (1024*1024)
                print(f"📊 Tamaño JPEG: {jpeg_size:.2f} MB")
                
                # Limpiar archivo temporal (ignorar error de permisos en Windows)
                try:
                    temp_path.unlink()
                    print(f"✅ Archivo temporal eliminado")
                except PermissionError:
                    print(f"⚠️ No se pudo eliminar archivo temporal (normal en Windows)")
                
                return True
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"❌ Tipo: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Uso: python test_pdf_conversion.py <ruta_tiff>")
        sys.exit(1)
    
    tiff_path = Path(sys.argv[1])
    if not tiff_path.exists():
        print(f"❌ Error: El archivo {tiff_path} no existe")
        sys.exit(1)
    
    print("🧪 DIAGNÓSTICO DE CONVERSIÓN TIFF A JPEG")
    print("=" * 50)
    
    success = test_tiff_to_jpeg_conversion(tiff_path)
    
    if success:
        print("✅ Prueba completada exitosamente")
    else:
        print("❌ Prueba falló")
        sys.exit(1)

if __name__ == "__main__":
    main()
