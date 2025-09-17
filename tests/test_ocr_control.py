#!/usr/bin/env python3
"""
Test de Control de OCR
======================

Este test verifica la nueva funcionalidad de control de OCR:
1. PDFs con OCR habilitado (use_ocr: true)
2. PDFs sin OCR (use_ocr: false)
3. Verificación de que EasyOCR no se inicializa cuando está deshabilitado
4. Verificación de que los PDFs se crean correctamente en ambos casos

Autor: Sistema de Automatización y Digitalización
Fecha: 2024
"""

import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any
import time

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.converters.pdf_easyocr_converter import PDFEasyOCRConverter
from src.postconverters.consolidated_pdf_postconverter import ConsolidatedPDFPostconverter
from src.output_manager import output_manager


class OCRControlTest:
    """Test de control de OCR"""
    
    def __init__(self):
        self.test_dir = None
        self.input_dir = None
        self.output_dir = None
        
    def setup_test_environment(self) -> bool:
        """Configura el entorno de prueba"""
        try:
            # Crear directorio temporal
            self.test_dir = Path(tempfile.mkdtemp(prefix="ocr_control_test_"))
            self.input_dir = self.test_dir / "input"
            self.output_dir = self.test_dir / "output"
            
            # Crear directorios
            self.input_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivo de prueba
            test_file = "test_input/test_document.tiff"
            if Path(test_file).exists():
                shutil.copy2(test_file, self.input_dir)
                output_manager.info(f"✅ Archivo de prueba copiado: {test_file}")
                return True
            else:
                output_manager.warning(f"⚠️ Archivo de prueba no encontrado: {test_file}")
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error configurando entorno de prueba: {str(e)}")
            return False
    
    def test_pdf_with_ocr_enabled(self) -> bool:
        """Test de PDF con OCR habilitado"""
        try:
            output_manager.info("🧪 Probando PDF con OCR habilitado...")
            
            # Configuración con OCR habilitado
            config = {
                "enabled": True,
                "resolution": 300,
                "page_size": "A4",
                "fit_to_page": True,
                "ocr_language": ["es"],
                "ocr_confidence": 0.5,
                "create_searchable_pdf": True,
                "use_ocr": True,  # OCR habilitado
                "use_gpu": False,
                "compression": {
                    "enabled": False
                }
            }
            
            # Crear conversor
            converter = PDFEasyOCRConverter(config)
            
            # Verificar que OCR está habilitado
            assert converter.use_ocr == True, "OCR debería estar habilitado"
            assert converter.create_searchable_pdf == True, "PDF buscable debería estar habilitado"
            
            # Verificar que EasyOCR se inicializó (puede ser None si no está instalado)
            if converter.ocr_reader is not None:
                output_manager.info("✅ EasyOCR inicializado correctamente")
            else:
                output_manager.warning("⚠️ EasyOCR no disponible (puede no estar instalado)")
            
            # Procesar archivo
            input_file = list(self.input_dir.glob("*.tiff"))[0]
            output_file = self.output_dir / "test_with_ocr.pdf"
            
            success = converter.convert(input_file, output_file)
            
            if success and output_file.exists():
                output_manager.success("✅ PDF con OCR creado exitosamente")
                return True
            else:
                output_manager.error("❌ Error creando PDF con OCR")
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error en test de PDF con OCR: {str(e)}")
            return False
    
    def test_pdf_with_ocr_disabled(self) -> bool:
        """Test de PDF sin OCR"""
        try:
            output_manager.info("🧪 Probando PDF sin OCR...")
            
            # Configuración con OCR deshabilitado
            config = {
                "enabled": True,
                "resolution": 300,
                "page_size": "A4",
                "fit_to_page": True,
                "ocr_language": ["es"],
                "ocr_confidence": 0.5,
                "create_searchable_pdf": False,
                "use_ocr": False,  # OCR deshabilitado
                "use_gpu": False,
                "compression": {
                    "enabled": False
                }
            }
            
            # Crear conversor
            converter = PDFEasyOCRConverter(config)
            
            # Verificar que OCR está deshabilitado
            assert converter.use_ocr == False, "OCR debería estar deshabilitado"
            assert converter.ocr_reader is None, "EasyOCR no debería estar inicializado"
            
            output_manager.info("✅ OCR correctamente deshabilitado")
            
            # Procesar archivo
            input_file = list(self.input_dir.glob("*.tiff"))[0]
            output_file = self.output_dir / "test_without_ocr.pdf"
            
            success = converter.convert(input_file, output_file)
            
            if success and output_file.exists():
                output_manager.success("✅ PDF sin OCR creado exitosamente")
                return True
            else:
                output_manager.error("❌ Error creando PDF sin OCR")
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error en test de PDF sin OCR: {str(e)}")
            return False
    
    def test_consolidated_pdf_with_ocr_control(self) -> bool:
        """Test de PDF consolidado con control de OCR"""
        try:
            output_manager.info("🧪 Probando PDF consolidado con control de OCR...")
            
            # Configuración con OCR deshabilitado
            config = {
                "enabled": True,
                "max_size_mb": 10,
                "output_folder": "PDF",
                "use_ocr": False,  # OCR deshabilitado en consolidación
                "sort_by_name": True,
                "resolution": 300,
                "page_size": "A4",
                "fit_to_page": True,
                "ocr_language": ["es"],
                "ocr_confidence": 0.5,
                "create_searchable_pdf": False,
                "use_gpu": False,
                "compression": {
                    "enabled": False
                }
            }
            
            # Crear postconversor
            postconverter = ConsolidatedPDFPostconverter(config)
            
            # Verificar que OCR está deshabilitado
            assert postconverter.use_ocr == False, "OCR debería estar deshabilitado en postconversor"
            assert postconverter.pdf_converter.use_ocr == False, "OCR debería estar deshabilitado en conversor PDF"
            
            output_manager.success("✅ PDF consolidado con OCR deshabilitado configurado correctamente")
            return True
                
        except Exception as e:
            output_manager.error(f"❌ Error en test de PDF consolidado: {str(e)}")
            return False
    
    def test_performance_comparison(self) -> bool:
        """Test de comparación de rendimiento"""
        try:
            output_manager.info("⚡ Probando comparación de rendimiento...")
            
            input_file = list(self.input_dir.glob("*.tiff"))[0]
            
            # Test con OCR habilitado
            config_with_ocr = {
                "enabled": True,
                "resolution": 300,
                "use_ocr": True,
                "create_searchable_pdf": True,
                "compression": {"enabled": False}
            }
            
            converter_with_ocr = PDFEasyOCRConverter(config_with_ocr)
            output_file_with_ocr = self.output_dir / "performance_with_ocr.pdf"
            
            start_time = time.time()
            success_with_ocr = converter_with_ocr.convert(input_file, output_file_with_ocr)
            time_with_ocr = time.time() - start_time
            
            # Test sin OCR
            config_without_ocr = {
                "enabled": True,
                "resolution": 300,
                "use_ocr": False,
                "create_searchable_pdf": False,
                "compression": {"enabled": False}
            }
            
            converter_without_ocr = PDFEasyOCRConverter(config_without_ocr)
            output_file_without_ocr = self.output_dir / "performance_without_ocr.pdf"
            
            start_time = time.time()
            success_without_ocr = converter_without_ocr.convert(input_file, output_file_without_ocr)
            time_without_ocr = time.time() - start_time
            
            # Mostrar resultados
            output_manager.info(f"📊 Comparación de rendimiento:")
            output_manager.info(f"   Con OCR: {time_with_ocr:.2f} segundos")
            output_manager.info(f"   Sin OCR: {time_without_ocr:.2f} segundos")
            
            if time_without_ocr < time_with_ocr:
                speedup = time_with_ocr / time_without_ocr
                output_manager.info(f"   🚀 Mejora de velocidad: {speedup:.1f}x más rápido sin OCR")
            
            if success_with_ocr and success_without_ocr:
                output_manager.success("✅ Comparación de rendimiento completada")
                return True
            else:
                output_manager.error("❌ Error en comparación de rendimiento")
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error en test de rendimiento: {str(e)}")
            return False
    
    def cleanup(self):
        """Limpia el entorno de prueba"""
        try:
            if self.test_dir and self.test_dir.exists():
                shutil.rmtree(self.test_dir)
                output_manager.info(f"🧹 Entorno de prueba limpiado: {self.test_dir}")
        except Exception as e:
            output_manager.warning(f"⚠️ Error limpiando entorno: {str(e)}")
    
    def run_complete_test(self) -> bool:
        """Ejecuta el test completo de control de OCR"""
        try:
            output_manager.info("🚀 Iniciando test de control de OCR...")
            start_time = time.time()
            
            # Configurar entorno
            if not self.setup_test_environment():
                return False
            
            # Ejecutar tests
            tests = [
                ("PDF con OCR habilitado", self.test_pdf_with_ocr_enabled),
                ("PDF sin OCR", self.test_pdf_with_ocr_disabled),
                ("PDF consolidado con control OCR", self.test_consolidated_pdf_with_ocr_control),
                ("Comparación de rendimiento", self.test_performance_comparison)
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                output_manager.info(f"🧪 Ejecutando test: {test_name}")
                if test_func():
                    passed_tests += 1
                    output_manager.success(f"✅ Test {test_name} PASÓ")
                else:
                    output_manager.error(f"❌ Test {test_name} FALLÓ")
            
            # Calcular tiempo total
            end_time = time.time()
            total_time = end_time - start_time
            
            # Mostrar resultados
            output_manager.info("=" * 60)
            output_manager.info("📊 RESULTADOS DEL TEST DE CONTROL DE OCR")
            output_manager.info("=" * 60)
            output_manager.info(f"✅ Tests pasados: {passed_tests}/{total_tests}")
            output_manager.info(f"⏱️ Tiempo total: {total_time:.2f} segundos")
            
            if passed_tests == total_tests:
                output_manager.success("🎉 ¡TODOS LOS TESTS DE CONTROL DE OCR PASARON!")
                return True
            else:
                output_manager.error(f"❌ {total_tests - passed_tests} tests fallaron")
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error en test de control de OCR: {str(e)}")
            return False
        finally:
            self.cleanup()


def main():
    """Función principal"""
    try:
        output_manager.info("🧪 Test de Control de OCR")
        output_manager.info("=" * 60)
        
        # Crear y ejecutar test
        ocr_test = OCRControlTest()
        success = ocr_test.run_complete_test()
        
        if success:
            output_manager.success("🎉 ¡TEST DE CONTROL DE OCR COMPLETADO EXITOSAMENTE!")
            sys.exit(0)
        else:
            output_manager.error("❌ TEST DE CONTROL DE OCR FALLÓ")
            sys.exit(1)
            
    except Exception as e:
        output_manager.error(f"❌ Error crítico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
