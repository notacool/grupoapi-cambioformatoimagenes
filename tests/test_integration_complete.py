#!/usr/bin/env python3
"""
Test de Integración Completo
============================

Este test verifica todo el flujo del sistema:
1. Configuración y validación
2. Procesamiento de archivos TIFF
3. Conversión a múltiples formatos
4. Postconversión (PDF consolidado y MET)
5. Validación de salidas

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

from src.converter import TIFFConverter
from src.config_manager import ConfigManager
from src.file_processor import FileProcessor
from src.output_manager import output_manager


class IntegrationTest:
    """Test de integración completo del sistema"""
    
    def __init__(self):
        self.test_dir = None
        self.input_dir = None
        self.output_dir = None
        self.config_manager = None
        self.tiff_converter = None
        self.file_processor = None
        
    def setup_test_environment(self) -> bool:
        """Configura el entorno de prueba"""
        try:
            # Crear directorio temporal
            self.test_dir = Path(tempfile.mkdtemp(prefix="integration_test_"))
            self.input_dir = self.test_dir / "input"
            self.output_dir = self.test_dir / "output"
            
            # Crear directorios
            self.input_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivos de prueba
            test_files = [
                "test_input/test_document.tiff",
                "test_input/test.tiff"
            ]
            
            for test_file in test_files:
                if Path(test_file).exists():
                    shutil.copy2(test_file, self.input_dir)
                    output_manager.info(f"✅ Archivo de prueba copiado: {test_file}")
                else:
                    output_manager.warning(f"⚠️ Archivo de prueba no encontrado: {test_file}")
            
            # Crear subcarpetas de prueba
            subfolder = self.input_dir / "test_subfolder"
            subfolder.mkdir(exist_ok=True)
            
            # Copiar archivos TIFF a subcarpeta
            tiff_files = [
                "test_input/test_subfolder/TIFF/test_00.tiff",
                "test_input/test_subfolder/TIFF/test_01.tiff",
                "test_input/test_subfolder/TIFF/test_02.tiff"
            ]
            
            tiff_dir = subfolder / "TIFF"
            tiff_dir.mkdir(exist_ok=True)
            
            for tiff_file in tiff_files:
                if Path(tiff_file).exists():
                    shutil.copy2(tiff_file, tiff_dir)
                    output_manager.info(f"✅ Archivo TIFF copiado: {tiff_file}")
            
            output_manager.success(f"✅ Entorno de prueba configurado en: {self.test_dir}")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error configurando entorno de prueba: {str(e)}")
            return False
    
    def test_configuration(self) -> bool:
        """Test de configuración del sistema"""
        try:
            output_manager.info("🔧 Probando configuración del sistema...")
            
            # Inicializar config manager
            self.config_manager = ConfigManager("config.yaml")
            
            # Verificar configuración
            assert self.config_manager is not None, "ConfigManager no inicializado"
            
            # Verificar formatos habilitados
            enabled_formats = self.config_manager.get_enabled_formats()
            output_manager.info(f"📋 Formatos habilitados: {enabled_formats}")
            
            # Verificar configuración específica (TIFF es el formato de entrada, no de salida)
            # Los formatos de salida son JPGHIGH, JPGLOW, PDF, MET
            
            jpg_high_config = self.config_manager.get_format_config("JPGHIGH")
            assert jpg_high_config is not None, "Configuración JPGHIGH no encontrada"
            assert jpg_high_config.get("enabled", False), "JPGHIGH no está habilitado"
            
            pdf_config = self.config_manager.get_format_config("PDF")
            assert pdf_config is not None, "Configuración PDF no encontrada"
            assert pdf_config.get("enabled", False), "PDF no está habilitado"
            
            output_manager.success("✅ Configuración del sistema validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de configuración: {str(e)}")
            return False
    
    def test_file_processing(self) -> bool:
        """Test de procesamiento de archivos"""
        try:
            output_manager.info("📁 Probando procesamiento de archivos...")
            
            # Inicializar file processor
            self.file_processor = FileProcessor(str(self.input_dir), str(self.output_dir))
            
            # Procesar archivos
            files_to_process = list(self.input_dir.glob("**/*.tiff"))
            output_manager.info(f"📋 Archivos encontrados: {len(files_to_process)}")
            
            for file_path in files_to_process:
                output_manager.info(f"🔄 Procesando: {file_path.name}")
                
                # Verificar que el archivo existe y es válido
                assert file_path.exists(), f"Archivo no existe: {file_path}"
                assert file_path.stat().st_size > 0, f"Archivo vacío: {file_path}"
                
                # Verificar que es un archivo TIFF
                assert file_path.suffix.lower() == '.tiff', f"No es un archivo TIFF: {file_path}"
            
            output_manager.success("✅ Procesamiento de archivos validado")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de procesamiento: {str(e)}")
            return False
    
    def test_conversion(self) -> bool:
        """Test de conversión de archivos"""
        try:
            output_manager.info("🔄 Probando conversión de archivos...")
            
            # Inicializar converter
            self.tiff_converter = TIFFConverter()
            
            # Verificar que hay archivos TIFF para procesar
            files_to_process = list(self.input_dir.glob("**/*.tiff"))
            assert len(files_to_process) > 0, "No hay archivos TIFF para procesar"
            
            output_manager.info(f"📋 Archivos TIFF encontrados: {len(files_to_process)}")
            
            # Convertir directorio completo (solo una vez)
            output_manager.info("🔄 Ejecutando conversión completa...")
            result = self.tiff_converter.convert_directory(str(self.input_dir), str(self.output_dir))
            
            # Verificar resultado
            assert result is not None, "Conversión falló"
            assert result.get("success", False), "Conversión no exitosa"
            
            # Verificar que se generaron archivos de salida
            output_files = list(self.output_dir.glob("**/*"))
            output_files = [f for f in output_files if f.is_file()]
            assert len(output_files) > 0, "No se generaron archivos de salida"
            
            output_manager.info(f"📋 Archivos de salida generados: {len(output_files)}")
            
            output_manager.success("✅ Conversión de archivos validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de conversión: {str(e)}")
            return False
    
    def test_postconversion(self) -> bool:
        """Test de postconversión"""
        try:
            output_manager.info("📄 Probando postconversión...")
            
            # Verificar que se generaron archivos PDF
            pdf_files = list(self.output_dir.glob("**/*.pdf"))
            output_manager.info(f"📋 Archivos PDF encontrados: {len(pdf_files)}")
            
            if pdf_files:
                # Verificar que los PDFs son válidos
                for pdf_file in pdf_files:
                    assert pdf_file.exists(), f"PDF no existe: {pdf_file}"
                    assert pdf_file.stat().st_size > 0, f"PDF vacío: {pdf_file}"
                    
                    # Verificar que el nombre contiene el formato
                    assert "PDF" in pdf_file.name, f"Nombre de PDF incorrecto: {pdf_file.name}"
            
            # Verificar que se generaron archivos MET
            met_files = list(self.output_dir.glob("**/*.xml"))
            output_manager.info(f"📋 Archivos MET encontrados: {len(met_files)}")
            
            if met_files:
                # Verificar que los METs son válidos
                for met_file in met_files:
                    assert met_file.exists(), f"MET no existe: {met_file}"
                    assert met_file.stat().st_size > 0, f"MET vacío: {met_file}"
                    
                    # Verificar que el nombre contiene el formato
                    assert "MET" in met_file.name, f"Nombre de MET incorrecto: {met_file.name}"
            
            output_manager.success("✅ Postconversión validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de postconversión: {str(e)}")
            return False
    
    def test_output_structure(self) -> bool:
        """Test de estructura de salida"""
        try:
            output_manager.info("📁 Probando estructura de salida...")
            
            # Verificar estructura de directorios
            expected_dirs = ["JPGHIGH", "JPGLOW", "PDF", "METS"]
            
            for expected_dir in expected_dirs:
                dir_path = self.output_dir / expected_dir
                if dir_path.exists():
                    output_manager.info(f"✅ Directorio encontrado: {expected_dir}")
                    
                    # Verificar que contiene archivos
                    files_in_dir = list(dir_path.glob("*"))
                    assert len(files_in_dir) > 0, f"Directorio vacío: {expected_dir}"
                    
                    for file_path in files_in_dir:
                        assert file_path.stat().st_size > 0, f"Archivo vacío en {expected_dir}: {file_path.name}"
                else:
                    output_manager.warning(f"⚠️ Directorio no encontrado: {expected_dir}")
            
            # Verificar archivos de log
            log_files = list(self.output_dir.glob("**/*.log"))
            if log_files:
                output_manager.info(f"📋 Archivos de log encontrados: {len(log_files)}")
                for log_file in log_files:
                    assert log_file.stat().st_size > 0, f"Log vacío: {log_file}"
            
            output_manager.success("✅ Estructura de salida validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de estructura: {str(e)}")
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
        """Ejecuta el test de integración completo"""
        try:
            output_manager.info("🚀 Iniciando test de integración completo...")
            start_time = time.time()
            
            # Configurar entorno
            if not self.setup_test_environment():
                return False
            
            # Ejecutar tests
            tests = [
                ("Configuración", self.test_configuration),
                ("Procesamiento", self.test_file_processing),
                ("Conversión", self.test_conversion),
                ("Postconversión", self.test_postconversion),
                ("Estructura", self.test_output_structure)
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
            output_manager.info("📊 RESULTADOS DEL TEST DE INTEGRACIÓN")
            output_manager.info("=" * 60)
            output_manager.info(f"✅ Tests pasados: {passed_tests}/{total_tests}")
            output_manager.info(f"⏱️ Tiempo total: {total_time:.2f} segundos")
            
            if passed_tests == total_tests:
                output_manager.success("🎉 ¡TODOS LOS TESTS PASARON!")
                return True
            else:
                output_manager.error(f"❌ {total_tests - passed_tests} tests fallaron")
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error en test de integración: {str(e)}")
            return False
        finally:
            self.cleanup()


def main():
    """Función principal"""
    try:
        output_manager.info("🧪 Test de Integración Completo del Sistema")
        output_manager.info("=" * 60)
        
        # Crear y ejecutar test
        integration_test = IntegrationTest()
        success = integration_test.run_complete_test()
        
        if success:
            output_manager.success("🎉 ¡TEST DE INTEGRACIÓN COMPLETADO EXITOSAMENTE!")
            sys.exit(0)
        else:
            output_manager.error("❌ TEST DE INTEGRACIÓN FALLÓ")
            sys.exit(1)
            
    except Exception as e:
        output_manager.error(f"❌ Error crítico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
