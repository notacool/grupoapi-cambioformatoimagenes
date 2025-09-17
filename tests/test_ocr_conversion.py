#!/usr/bin/env python3
"""
Script de prueba para diagnosticar el problema de OCR
"""

import sys
from pathlib import Path
from PIL import Image
import tempfile
import time
import easyocr

def test_ocr_on_image(tiff_path):
    """Prueba el OCR en una imagen paso a paso"""
    print(f"🔍 Probando OCR: {tiff_path}")
    
    try:
        # Paso 1: Inicializar EasyOCR
        print("🔄 Paso 1: Inicializando EasyOCR...")
        start_time = time.time()
        
        reader = easyocr.Reader(['es'])
        print(f"✅ EasyOCR inicializado")
        print(f"⏱️ Tiempo inicialización: {time.time() - start_time:.2f} segundos")
        
        # Paso 2: Abrir imagen
        print("🔄 Paso 2: Abriendo imagen TIFF...")
        start_time = time.time()
        
        with Image.open(tiff_path) as pil_img:
            print(f"✅ Imagen abierta: {pil_img.size[0]}x{pil_img.size[1]} px, modo: {pil_img.mode}")
            print(f"⏱️ Tiempo apertura: {time.time() - start_time:.2f} segundos")
            
            # Paso 3: Convertir a RGB si es necesario
            if pil_img.mode not in ["RGB", "L"]:
                print("🔄 Convirtiendo a RGB...")
                pil_img = pil_img.convert("RGB")
                print(f"✅ Conversión completada")
            
            # Paso 4: Crear archivo temporal JPEG
            print("🔄 Paso 3: Creando archivo temporal JPEG...")
            start_time = time.time()
            
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                
                pil_img.save(
                    temp_path,
                    format="JPEG",
                    quality=85,
                    optimize=True,
                )
                
                print(f"✅ JPEG temporal creado: {temp_path}")
                print(f"⏱️ Tiempo guardado: {time.time() - start_time:.2f} segundos")
                
                # Paso 5: Procesar OCR
                print("🔄 Paso 4: Procesando OCR...")
                start_time = time.time()
                
                # Convertir PIL a numpy array para EasyOCR
                import numpy as np
                img_array = np.array(pil_img)
                
                print(f"✅ Imagen convertida a numpy array: {img_array.shape}")
                
                # Ejecutar OCR
                results = reader.readtext(img_array)
                
                print(f"✅ OCR completado")
                print(f"⏱️ Tiempo OCR: {time.time() - start_time:.2f} segundos")
                print(f"📊 Texto detectado: {len(results)} elementos")
                
                # Mostrar algunos resultados
                for i, (bbox, text, confidence) in enumerate(results[:3]):
                    print(f"  {i+1}. '{text}' (confianza: {confidence:.2f})")
                
                # Limpiar archivo temporal
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
        print("Uso: python test_ocr_conversion.py <ruta_tiff>")
        sys.exit(1)
    
    tiff_path = Path(sys.argv[1])
    if not tiff_path.exists():
        print(f"❌ Error: El archivo {tiff_path} no existe")
        sys.exit(1)
    
    print("🧪 DIAGNÓSTICO DE OCR EN IMAGEN TIFF")
    print("=" * 50)
    
    success = test_ocr_on_image(tiff_path)
    
    if success:
        print("✅ Prueba de OCR completada exitosamente")
    else:
        print("❌ Prueba de OCR falló")
        sys.exit(1)

if __name__ == "__main__":
    main()

