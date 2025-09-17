#!/usr/bin/env python3
"""
Test de Integración Simplificado
================================

Este test verifica los componentes principales del sistema:
1. Configuración y validación
2. Inicialización de conversores
3. Estructura de archivos
4. Funcionalidad básica

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


class SimpleIntegrationTest:
    """Test de integración simplificado del sistema"""
    
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
            self.test_dir = Path(tempfile.mkdtemp(prefix="simple_integration_test_"))
            self.input_dir = self.test_dir / "input"
            self.output_dir = self.test_dir / "output"
            
            # Crear directorios
            self.input_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear subcarpeta de prueba
            subfolder = self.input_dir / "test_subfolder"
            subfolder.mkdir(exist_ok=True)
            
            # Crear carpeta TIFF
            tiff_dir = subfolder / "TIFF"
            tiff_dir.mkdir(exist_ok=True)
            
            # Crear archivos TIFF de prueba simples (archivos vacíos para testing)
            test_files = ["test_00.tiff", "test_01.tiff", "test_02.tiff"]
            for test_file in test_files:
                test_path = tiff_dir / test_file
                test_path.touch()  # Crear archivo vacío
                output_manager.info(f"✅ Archivo de prueba creado: {test_file}")
            
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
            
            # Verificar configuración específica
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
    
    def test_initialization(self) -> bool:
        """Test de inicialización de componentes"""
        try:
            output_manager.info("🚀 Probando inicialización de componentes...")
            
            # Inicializar TIFFConverter
            self.tiff_converter = TIFFConverter()
            assert self.tiff_converter is not None, "TIFFConverter no inicializado"
            assert self.tiff_converter.config_manager is not None, "ConfigManager no inicializado en TIFFConverter"
            
            # Verificar conversores inicializados
            assert hasattr(self.tiff_converter, 'converters'), "Converters no inicializados"
            assert hasattr(self.tiff_converter, 'postconverters'), "Postconverters no inicializados"
            
            # Inicializar FileProcessor
            self.file_processor = FileProcessor(str(self.input_dir), str(self.output_dir))
            assert self.file_processor is not None, "FileProcessor no inicializado"
            assert self.file_processor.input_dir == self.input_dir, "Input dir incorrecto en FileProcessor"
            assert self.file_processor.output_dir == self.output_dir, "Output dir incorrecto en FileProcessor"
            
            output_manager.success("✅ Inicialización de componentes validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de inicialización: {str(e)}")
            return False
    
    def test_file_structure(self) -> bool:
        """Test de estructura de archivos"""
        try:
            output_manager.info("📁 Probando estructura de archivos...")
            
            # Verificar estructura de entrada
            assert self.input_dir.exists(), "Directorio de entrada no existe"
            assert self.output_dir.exists(), "Directorio de salida no existe"
            
            # Verificar subcarpeta
            subfolder = self.input_dir / "test_subfolder"
            assert subfolder.exists(), "Subcarpeta no existe"
            
            # Verificar carpeta TIFF
            tiff_dir = subfolder / "TIFF"
            assert tiff_dir.exists(), "Carpeta TIFF no existe"
            
            # Verificar archivos TIFF
            tiff_files = list(tiff_dir.glob("*.tiff"))
            assert len(tiff_files) > 0, "No hay archivos TIFF"
            
            output_manager.info(f"📋 Archivos TIFF encontrados: {len(tiff_files)}")
            
            # Verificar que FileProcessor puede encontrar las carpetas TIFF
            tiff_folders = self.file_processor.find_tiff_folders()
            assert len(tiff_folders) > 0, "FileProcessor no encontró carpetas TIFF"
            
            output_manager.info(f"📋 Carpetas TIFF encontradas por FileProcessor: {len(tiff_folders)}")
            
            output_manager.success("✅ Estructura de archivos validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de estructura: {str(e)}")
            return False
    
    def test_conversion_structure(self) -> bool:
        """Test de estructura de conversión (sin ejecutar conversión real)"""
        try:
            output_manager.info("🔄 Probando estructura de conversión...")
            
            # Verificar que los conversores están configurados
            converters = self.tiff_converter.converters
            assert len(converters) > 0, "No hay conversores configurados"
            
            output_manager.info(f"📋 Conversores configurados: {list(converters.keys())}")
            
            # Verificar que los postconversores están configurados
            postconverters = self.tiff_converter.postconverters
            assert len(postconverters) > 0, "No hay postconversores configurados"
            
            output_manager.info(f"📋 Postconversores configurados: {list(postconverters.keys())}")
            
            # Verificar configuración de cada conversor
            for name, converter in converters.items():
                assert converter is not None, f"Conversor {name} es None"
                assert hasattr(converter, 'config'), f"Conversor {name} no tiene config"
                assert converter.config.get('enabled', False), f"Conversor {name} no está habilitado"
            
            # Verificar configuración de cada postconversor
            for name, postconverter in postconverters.items():
                assert postconverter is not None, f"Postconversor {name} es None"
                assert hasattr(postconverter, 'config'), f"Postconversor {name} no tiene config"
                assert postconverter.config.get('enabled', False), f"Postconversor {name} no está habilitado"
            
            output_manager.success("✅ Estructura de conversión validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de estructura de conversión: {str(e)}")
            return False
    
    def test_output_structure(self) -> bool:
        """Test de estructura de salida"""
        try:
            output_manager.info("📁 Probando estructura de salida...")
            
            # Verificar que el directorio de salida existe
            assert self.output_dir.exists(), "Directorio de salida no existe"
            
            # Verificar que se pueden crear subdirectorios
            test_dirs = ["JPGHIGH", "JPGLOW", "PDF", "METS"]
            for test_dir in test_dirs:
                test_path = self.output_dir / test_dir
                test_path.mkdir(exist_ok=True)
                assert test_path.exists(), f"No se pudo crear directorio: {test_dir}"
            
            output_manager.success("✅ Estructura de salida validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de estructura de salida: {str(e)}")
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
        """Ejecuta el test de integración simplificado"""
        try:
            output_manager.info("🚀 Iniciando test de integración simplificado...")
            start_time = time.time()
            
            # Configurar entorno
            if not self.setup_test_environment():
                return False
            
            # Ejecutar tests
            tests = [
                ("Configuración", self.test_configuration),
                ("Inicialización", self.test_initialization),
                ("Estructura de Archivos", self.test_file_structure),
                ("Estructura de Conversión", self.test_conversion_structure),
                ("Estructura de Salida", self.test_output_structure)
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
            output_manager.info("📊 RESULTADOS DEL TEST DE INTEGRACIÓN SIMPLIFICADO")
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
        output_manager.info("🧪 Test de Integración Simplificado del Sistema")
        output_manager.info("=" * 60)
        
        # Crear y ejecutar test
        integration_test = SimpleIntegrationTest()
        success = integration_test.run_complete_test()
        
        if success:
            output_manager.success("🎉 ¡TEST DE INTEGRACIÓN SIMPLIFICADO COMPLETADO EXITOSAMENTE!")
            sys.exit(0)
        else:
            output_manager.error("❌ TEST DE INTEGRACIÓN SIMPLIFICADO FALLÓ")
            sys.exit(1)
            
    except Exception as e:
        output_manager.error(f"❌ Error crítico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
