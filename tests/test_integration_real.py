#!/usr/bin/env python3
"""
Test de Integración con Archivos Reales
========================================

Este test verifica el flujo completo del sistema usando archivos TIFF reales:
1. Configuración y validación
2. Procesamiento de archivos TIFF reales
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


class RealIntegrationTest:
    """Test de integración con archivos reales"""
    
    def __init__(self):
        self.test_dir = None
        self.input_dir = None
        self.output_dir = None
        self.config_manager = None
        self.tiff_converter = None
        self.file_processor = None
        
    def setup_test_environment(self) -> bool:
        """Configura el entorno de prueba con archivos reales"""
        try:
            # Crear directorio temporal
            self.test_dir = Path(tempfile.mkdtemp(prefix="real_integration_test_"))
            self.input_dir = self.test_dir / "input"
            self.output_dir = self.test_dir / "output"
            
            # Crear directorios
            self.input_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Buscar archivos TIFF reales en el proyecto
            real_tiff_files = []
            
            # Buscar en test_input
            test_input_dir = Path("test_input")
            if test_input_dir.exists():
                real_tiff_files.extend(list(test_input_dir.glob("**/*.tiff")))
            
            # Buscar en test_outputs
            test_outputs_dir = Path("test_outputs")
            if test_outputs_dir.exists():
                real_tiff_files.extend(list(test_outputs_dir.glob("**/*.tiff")))
            
            # Buscar en el directorio raíz
            real_tiff_files.extend(list(Path(".").glob("*.tiff")))
            
            if not real_tiff_files:
                output_manager.warning("⚠️ No se encontraron archivos TIFF reales para el test")
                return False
            
            # Crear subcarpeta de prueba
            subfolder = self.input_dir / "test_subfolder"
            subfolder.mkdir(exist_ok=True)
            
            # Crear carpeta TIFF
            tiff_dir = subfolder / "TIFF"
            tiff_dir.mkdir(exist_ok=True)
            
            # Copiar archivos TIFF reales (máximo 3 para el test)
            copied_files = 0
            for tiff_file in real_tiff_files[:3]:  # Limitar a 3 archivos
                if tiff_file.exists() and tiff_file.stat().st_size > 0:
                    dest_file = tiff_dir / f"test_{copied_files:02d}.tiff"
                    shutil.copy2(tiff_file, dest_file)
                    output_manager.info(f"✅ Archivo TIFF real copiado: {tiff_file.name} -> {dest_file.name}")
                    copied_files += 1
            
            if copied_files == 0:
                output_manager.warning("⚠️ No se pudieron copiar archivos TIFF válidos")
                return False
            
            output_manager.success(f"✅ Entorno de prueba configurado con {copied_files} archivos TIFF reales")
            output_manager.info(f"📁 Directorio de prueba: {self.test_dir}")
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
            
            # Verificar que hay al menos un formato habilitado
            assert len(enabled_formats) > 0, "No hay formatos habilitados"
            
            output_manager.success("✅ Configuración del sistema validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de configuración: {str(e)}")
            return False
    
    def test_conversion(self) -> bool:
        """Test de conversión con archivos reales"""
        try:
            output_manager.info("🔄 Probando conversión con archivos reales...")
            
            # Inicializar converter
            self.tiff_converter = TIFFConverter()
            
            # Verificar que hay archivos TIFF para procesar
            files_to_process = list(self.input_dir.glob("**/*.tiff"))
            assert len(files_to_process) > 0, "No hay archivos TIFF para procesar"
            
            output_manager.info(f"📋 Archivos TIFF encontrados: {len(files_to_process)}")
            
            # Mostrar información de los archivos
            for file_path in files_to_process:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                output_manager.info(f"📄 {file_path.name}: {size_mb:.2f} MB")
            
            # Convertir directorio completo
            output_manager.info("🔄 Ejecutando conversión completa...")
            start_time = time.time()
            
            result = self.tiff_converter.convert_directory(str(self.input_dir), str(self.output_dir))
            
            end_time = time.time()
            conversion_time = end_time - start_time
            
            # Verificar resultado
            assert result is not None, "Conversión falló"
            assert result.get("success", False), "Conversión no exitosa"
            
            # Verificar que se generaron archivos de salida
            output_files = list(self.output_dir.glob("**/*"))
            output_files = [f for f in output_files if f.is_file()]
            assert len(output_files) > 0, "No se generaron archivos de salida"
            
            output_manager.info(f"📋 Archivos de salida generados: {len(output_files)}")
            output_manager.info(f"⏱️ Tiempo de conversión: {conversion_time:.2f} segundos")
            
            # Mostrar información de archivos generados
            for output_file in output_files:
                size_mb = output_file.stat().st_size / (1024 * 1024)
                output_manager.info(f"📄 {output_file.name}: {size_mb:.2f} MB")
            
            output_manager.success("✅ Conversión con archivos reales validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de conversión: {str(e)}")
            return False
    
    def test_output_validation(self) -> bool:
        """Test de validación de salidas"""
        try:
            output_manager.info("📄 Probando validación de salidas...")
            
            # Verificar archivos PDF
            pdf_files = list(self.output_dir.glob("**/*.pdf"))
            if pdf_files:
                output_manager.info(f"📋 Archivos PDF encontrados: {len(pdf_files)}")
                for pdf_file in pdf_files:
                    assert pdf_file.stat().st_size > 0, f"PDF vacío: {pdf_file.name}"
                    output_manager.info(f"✅ PDF válido: {pdf_file.name}")
            
            # Verificar archivos JPG
            jpg_files = list(self.output_dir.glob("**/*.jpg"))
            if jpg_files:
                output_manager.info(f"📋 Archivos JPG encontrados: {len(jpg_files)}")
                for jpg_file in jpg_files:
                    assert jpg_file.stat().st_size > 0, f"JPG vacío: {jpg_file.name}"
                    output_manager.info(f"✅ JPG válido: {jpg_file.name}")
            
            # Verificar archivos MET
            met_files = list(self.output_dir.glob("**/*.xml"))
            if met_files:
                output_manager.info(f"📋 Archivos MET encontrados: {len(met_files)}")
                for met_file in met_files:
                    assert met_file.stat().st_size > 0, f"MET vacío: {met_file.name}"
                    output_manager.info(f"✅ MET válido: {met_file.name}")
            
            # Verificar archivos de log
            log_files = list(self.output_dir.glob("**/*.log"))
            if log_files:
                output_manager.info(f"📋 Archivos de log encontrados: {len(log_files)}")
                for log_file in log_files:
                    assert log_file.stat().st_size > 0, f"Log vacío: {log_file.name}"
                    output_manager.info(f"✅ Log válido: {log_file.name}")
            
            output_manager.success("✅ Validación de salidas completada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de validación: {str(e)}")
            return False
    
    def test_performance(self) -> bool:
        """Test de rendimiento"""
        try:
            output_manager.info("⚡ Probando rendimiento...")
            
            # Calcular estadísticas de rendimiento
            input_files = list(self.input_dir.glob("**/*.tiff"))
            output_files = list(self.output_dir.glob("**/*"))
            output_files = [f for f in output_files if f.is_file()]
            
            # Calcular tamaños
            total_input_size = sum(f.stat().st_size for f in input_files)
            total_output_size = sum(f.stat().st_size for f in output_files)
            
            input_size_mb = total_input_size / (1024 * 1024)
            output_size_mb = total_output_size / (1024 * 1024)
            
            # Calcular ratio de compresión
            if total_input_size > 0:
                compression_ratio = (total_output_size / total_input_size) * 100
            else:
                compression_ratio = 0
            
            output_manager.info(f"📊 Estadísticas de rendimiento:")
            output_manager.info(f"   📥 Tamaño de entrada: {input_size_mb:.2f} MB")
            output_manager.info(f"   📤 Tamaño de salida: {output_size_mb:.2f} MB")
            output_manager.info(f"   📈 Ratio de compresión: {compression_ratio:.1f}%")
            output_manager.info(f"   📁 Archivos de entrada: {len(input_files)}")
            output_manager.info(f"   📁 Archivos de salida: {len(output_files)}")
            
            output_manager.success("✅ Test de rendimiento completado")
            return True
            
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
        """Ejecuta el test de integración con archivos reales"""
        try:
            output_manager.info("🚀 Iniciando test de integración con archivos reales...")
            start_time = time.time()
            
            # Configurar entorno
            if not self.setup_test_environment():
                output_manager.warning("⚠️ No se pudo configurar el entorno con archivos reales")
                return False
            
            # Ejecutar tests
            tests = [
                ("Configuración", self.test_configuration),
                ("Conversión", self.test_conversion),
                ("Validación de Salidas", self.test_output_validation),
                ("Rendimiento", self.test_performance)
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
            output_manager.info("📊 RESULTADOS DEL TEST DE INTEGRACIÓN CON ARCHIVOS REALES")
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
        output_manager.info("🧪 Test de Integración con Archivos Reales")
        output_manager.info("=" * 60)
        
        # Crear y ejecutar test
        integration_test = RealIntegrationTest()
        success = integration_test.run_complete_test()
        
        if success:
            output_manager.success("🎉 ¡TEST DE INTEGRACIÓN CON ARCHIVOS REALES COMPLETADO EXITOSAMENTE!")
            sys.exit(0)
        else:
            output_manager.error("❌ TEST DE INTEGRACIÓN CON ARCHIVOS REALES FALLÓ")
            sys.exit(1)
            
    except Exception as e:
        output_manager.error(f"❌ Error crítico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
