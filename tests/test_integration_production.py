#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Integracion con Carpeta de Produccion
=============================================

Este test verifica el flujo completo del sistema usando la carpeta de produccion:
C:\\Users\\Roman\\Desktop\\Pruebas Tifff\\230_1

1. Configuracion y validacion
2. Procesamiento de archivos TIFF de produccion
3. Conversion a multiples formatos
4. Postconversion (PDF consolidado y MET)
5. Validacion de salidas

Autor: Sistema de Automatizacion y Digitalizacion
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


class ProductionIntegrationTest:
    """Test de integracion con carpeta de produccion"""
    
    def __init__(self, production_path: str):
        self.production_path = Path(production_path)
        self.output_dir = None
        self.config_manager = None
        self.tiff_converter = None
        self.file_processor = None
        
    def validate_production_folder(self) -> bool:
        """Valida que la carpeta de produccion existe y contiene archivos TIFF"""
        try:
            output_manager.info(f"🔍 Validando carpeta de produccion: {self.production_path}")
            
            # Verificar que la carpeta existe
            if not self.production_path.exists():
                output_manager.error(f"❌ La carpeta no existe: {self.production_path}")
                return False
            
            if not self.production_path.is_dir():
                output_manager.error(f"❌ La ruta no es un directorio: {self.production_path}")
                return False
            
            # Buscar archivos TIFF
            tiff_files = list(self.production_path.glob("**/*.tiff"))
            tiff_files.extend(list(self.production_path.glob("**/*.tif")))
            
            if not tiff_files:
                output_manager.error(f"❌ No se encontraron archivos TIFF en: {self.production_path}")
                return False
            
            # Filtrar archivos validos (no vacios)
            valid_tiff_files = [f for f in tiff_files if f.stat().st_size > 0]
            
            if not valid_tiff_files:
                output_manager.error(f"❌ No se encontraron archivos TIFF validos en: {self.production_path}")
                return False
            
            output_manager.success(f"✅ Carpeta de produccion validada")
            output_manager.info(f"📁 Archivos TIFF encontrados: {len(valid_tiff_files)}")
            
            # Mostrar informacion de los archivos
            total_size = 0
            for i, tiff_file in enumerate(valid_tiff_files[:10]):  # Mostrar solo los primeros 10
                size_mb = tiff_file.stat().st_size / (1024 * 1024)
                total_size += tiff_file.stat().st_size
                output_manager.info(f"📄 {tiff_file.name}: {size_mb:.2f} MB")
            
            if len(valid_tiff_files) > 10:
                output_manager.info(f"📄 ... y {len(valid_tiff_files) - 10} archivos mas")
            
            total_size_mb = total_size / (1024 * 1024)
            output_manager.info(f"📊 Tamaño total: {total_size_mb:.2f} MB")
            
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error validando carpeta de produccion: {str(e)}")
            return False
    
    def setup_output_directory(self) -> bool:
        """Configura el directorio de salida"""
        try:
            # Crear directorio de salida junto a la carpeta de produccion
            parent_dir = self.production_path.parent
            import time
            timestamp = int(time.time())
            output_name = f"{self.production_path.name}_output_test_{timestamp}"
            self.output_dir = parent_dir / output_name
            
            # Limpiar directorio de salida si existe
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
                output_manager.info(f"🧹 Directorio de salida limpiado: {self.output_dir}")
            
            # Crear directorio de salida
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_manager.success(f"✅ Directorio de salida configurado: {self.output_dir}")
            
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error configurando directorio de salida: {str(e)}")
            return False
    
    def test_configuration(self) -> bool:
        """Test de configuracion del sistema"""
        try:
            output_manager.info("🔧 Probando configuracion del sistema...")
            
            # Inicializar config manager
            self.config_manager = ConfigManager("config.yaml")
            
            # Verificar configuracion
            assert self.config_manager is not None, "ConfigManager no inicializado"
            
            # Verificar formatos habilitados
            enabled_formats = self.config_manager.get_enabled_formats()
            output_manager.info(f"📋 Formatos habilitados: {enabled_formats}")
            
            # Verificar que hay al menos un formato habilitado
            assert len(enabled_formats) > 0, "No hay formatos habilitados"
            
            # Verificar configuracion especifica
            pdf_config = self.config_manager.get_format_config("PDF")
            if pdf_config.get("enabled", False):
                output_manager.info(f"📄 PDF habilitado: resolucion {pdf_config.get('resolution', 'N/A')}")
            
            jpg_config = self.config_manager.get_format_config("JPGHIGH")
            if jpg_config.get("enabled", False):
                output_manager.info(f"🖼️ JPGHIGH habilitado: calidad {jpg_config.get('quality', 'N/A')}")
            
            # Verificar postconversores
            postconverters = self.config_manager.get_postconverters_config()
            if postconverters:
                output_manager.info(f"🔄 Postconversores configurados: {list(postconverters.keys())}")
            
            output_manager.success("✅ Configuracion del sistema validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de configuracion: {str(e)}")
            return False
    
    def test_conversion(self) -> bool:
        """Test de conversion con archivos de produccion"""
        try:
            output_manager.info("🔄 Probando conversion con archivos de produccion...")
            
            # Inicializar converter
            self.tiff_converter = TIFFConverter()
            
            # Verificar que hay archivos TIFF para procesar
            tiff_files = list(self.production_path.glob("**/*.tiff"))
            tiff_files.extend(list(self.production_path.glob("**/*.tif")))
            valid_tiff_files = [f for f in tiff_files if f.stat().st_size > 0]
            
            assert len(valid_tiff_files) > 0, "No hay archivos TIFF validos para procesar"
            
            output_manager.info(f"📋 Archivos TIFF a procesar: {len(valid_tiff_files)}")
            
            # Convertir directorio completo
            output_manager.info("🔄 Ejecutando conversion completa...")
            start_time = time.time()
            
            result = self.tiff_converter.convert_directory(str(self.production_path), str(self.output_dir))
            
            end_time = time.time()
            conversion_time = end_time - start_time
            
            # Verificar resultado
            assert result is not None, "Conversion fallo"
            assert result.get("success", False), "Conversion no exitosa"
            
            # Verificar que se generaron archivos de salida
            output_files = list(self.output_dir.glob("**/*"))
            output_files = [f for f in output_files if f.is_file()]
            assert len(output_files) > 0, "No se generaron archivos de salida"
            
            output_manager.info(f"📋 Archivos de salida generados: {len(output_files)}")
            output_manager.info(f"⏱️ Tiempo de conversion: {conversion_time:.2f} segundos")
            
            # Mostrar informacion de archivos generados por tipo
            pdf_files = [f for f in output_files if f.suffix.lower() == '.pdf']
            jpg_files = [f for f in output_files if f.suffix.lower() in ['.jpg', '.jpeg']]
            xml_files = [f for f in output_files if f.suffix.lower() == '.xml']
            log_files = [f for f in output_files if f.suffix.lower() == '.log']
            
            if pdf_files:
                output_manager.info(f"📄 Archivos PDF generados: {len(pdf_files)}")
                for pdf_file in pdf_files[:5]:  # Mostrar solo los primeros 5
                    size_mb = pdf_file.stat().st_size / (1024 * 1024)
                    output_manager.info(f"   📄 {pdf_file.name}: {size_mb:.2f} MB")
            
            if jpg_files:
                output_manager.info(f"🖼️ Archivos JPG generados: {len(jpg_files)}")
            
            if xml_files:
                output_manager.info(f"📋 Archivos MET generados: {len(xml_files)}")
            
            if log_files:
                output_manager.info(f"📝 Archivos de log generados: {len(log_files)}")
            
            output_manager.success("✅ Conversion con archivos de produccion validada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de conversion: {str(e)}")
            return False
    
    def test_output_validation(self) -> bool:
        """Test de validacion de salidas"""
        try:
            output_manager.info("📄 Probando validacion de salidas...")
            
            # Verificar archivos PDF
            pdf_files = list(self.output_dir.glob("**/*.pdf"))
            if pdf_files:
                output_manager.info(f"📋 Archivos PDF encontrados: {len(pdf_files)}")
                for pdf_file in pdf_files:
                    assert pdf_file.stat().st_size > 0, f"PDF vacio: {pdf_file.name}"
                    size_mb = pdf_file.stat().st_size / (1024 * 1024)
                    output_manager.info(f"✅ PDF valido: {pdf_file.name} ({size_mb:.2f} MB)")
            
            # Verificar archivos JPG
            jpg_files = list(self.output_dir.glob("**/*.jpg"))
            jpg_files.extend(list(self.output_dir.glob("**/*.jpeg")))
            if jpg_files:
                output_manager.info(f"📋 Archivos JPG encontrados: {len(jpg_files)}")
                total_jpg_size = sum(f.stat().st_size for f in jpg_files)
                total_jpg_size_mb = total_jpg_size / (1024 * 1024)
                output_manager.info(f"✅ JPGs validos: {len(jpg_files)} archivos ({total_jpg_size_mb:.2f} MB total)")
            
            # Verificar archivos MET
            met_files = list(self.output_dir.glob("**/*.xml"))
            if met_files:
                output_manager.info(f"📋 Archivos MET encontrados: {len(met_files)}")
                for met_file in met_files:
                    assert met_file.stat().st_size > 0, f"MET vacio: {met_file.name}"
                    output_manager.info(f"✅ MET valido: {met_file.name}")
            
            # Verificar archivos de log
            log_files = list(self.output_dir.glob("**/*.log"))
            if log_files:
                output_manager.info(f"📋 Archivos de log encontrados: {len(log_files)}")
                for log_file in log_files:
                    assert log_file.stat().st_size > 0, f"Log vacio: {log_file.name}"
                    output_manager.info(f"✅ Log valido: {log_file.name}")
            
            # Verificar estructura de carpetas
            folders = [f for f in self.output_dir.glob("**/*") if f.is_dir()]
            if folders:
                output_manager.info(f"📁 Carpetas generadas: {len(folders)}")
                for folder in folders:
                    folder_files = list(folder.glob("*"))
                    folder_files = [f for f in folder_files if f.is_file()]
                    output_manager.info(f"   📁 {folder.name}: {len(folder_files)} archivos")
            
            output_manager.success("✅ Validacion de salidas completada")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de validacion: {str(e)}")
            return False
    
    def test_performance(self) -> bool:
        """Test de rendimiento"""
        try:
            output_manager.info("⚡ Probando rendimiento...")
            
            # Calcular estadisticas de rendimiento
            input_files = list(self.production_path.glob("**/*.tiff"))
            input_files.extend(list(self.production_path.glob("**/*.tif")))
            input_files = [f for f in input_files if f.stat().st_size > 0]
            
            output_files = list(self.output_dir.glob("**/*"))
            output_files = [f for f in output_files if f.is_file()]
            
            # Calcular tamanos
            total_input_size = sum(f.stat().st_size for f in input_files)
            total_output_size = sum(f.stat().st_size for f in output_files)
            
            input_size_mb = total_input_size / (1024 * 1024)
            output_size_mb = total_output_size / (1024 * 1024)
            
            # Calcular ratio de compresion
            if total_input_size > 0:
                compression_ratio = (total_output_size / total_input_size) * 100
            else:
                compression_ratio = 0
            
            # Calcular estadisticas por tipo de archivo
            pdf_files = [f for f in output_files if f.suffix.lower() == '.pdf']
            jpg_files = [f for f in output_files if f.suffix.lower() in ['.jpg', '.jpeg']]
            
            pdf_size = sum(f.stat().st_size for f in pdf_files) / (1024 * 1024)
            jpg_size = sum(f.stat().st_size for f in jpg_files) / (1024 * 1024)
            
            output_manager.info(f"📊 Estadisticas de rendimiento:")
            output_manager.info(f"   📥 Tamano de entrada: {input_size_mb:.2f} MB")
            output_manager.info(f"   📤 Tamano de salida: {output_size_mb:.2f} MB")
            output_manager.info(f"   📈 Ratio de compresion: {compression_ratio:.1f}%")
            output_manager.info(f"   📁 Archivos de entrada: {len(input_files)}")
            output_manager.info(f"   📁 Archivos de salida: {len(output_files)}")
            output_manager.info(f"   📄 Tamano PDFs: {pdf_size:.2f} MB")
            output_manager.info(f"   🖼️ Tamano JPGs: {jpg_size:.2f} MB")
            
            output_manager.success("✅ Test de rendimiento completado")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error en test de rendimiento: {str(e)}")
            return False
    
    def run_complete_test(self) -> bool:
        """Ejecuta el test de integracion con carpeta de produccion"""
        try:
            output_manager.info("🚀 Iniciando test de integracion con carpeta de produccion...")
            output_manager.info(f"📁 Carpeta de produccion: {self.production_path}")
            start_time = time.time()
            
            # Validar carpeta de produccion
            if not self.validate_production_folder():
                return False
            
            # Configurar directorio de salida
            if not self.setup_output_directory():
                return False
            
            # Ejecutar tests
            tests = [
                ("Configuracion", self.test_configuration),
                ("Conversion", self.test_conversion),
                ("Validacion de Salidas", self.test_output_validation),
                ("Rendimiento", self.test_performance)
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                output_manager.info(f"🧪 Ejecutando test: {test_name}")
                if test_func():
                    passed_tests += 1
                    output_manager.success(f"✅ Test {test_name} PASO")
                else:
                    output_manager.error(f"❌ Test {test_name} FALLO")
            
            # Calcular tiempo total
            end_time = time.time()
            total_time = end_time - start_time
            
            # Mostrar resultados
            output_manager.info("=" * 60)
            output_manager.info("📊 RESULTADOS DEL TEST DE INTEGRACION CON CARPETA DE PRODUCCION")
            output_manager.info("=" * 60)
            output_manager.info(f"📁 Carpeta de produccion: {self.production_path}")
            output_manager.info(f"📁 Carpeta de salida: {self.output_dir}")
            output_manager.info(f"✅ Tests pasados: {passed_tests}/{total_tests}")
            output_manager.info(f"⏱️ Tiempo total: {total_time:.2f} segundos")
            
            if passed_tests == total_tests:
                output_manager.success("🎉 ¡TODOS LOS TESTS PASARON!")
                output_manager.info(f"📁 Los archivos de salida estan en: {self.output_dir}")
                return True
            else:
                output_manager.error(f"❌ {total_tests - passed_tests} tests fallaron")
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error en test de integracion: {str(e)}")
            return False


def main():
    """Funcion principal"""
    try:
        # Carpeta de produccion especificada
        production_path = r"C:\Users\Román\Desktop\Pruebas Tifff\230_1"
        
        output_manager.info("🧪 Test de Integracion con Carpeta de Produccion")
        output_manager.info("=" * 60)
        output_manager.info(f"📁 Carpeta de produccion: {production_path}")
        
        # Crear y ejecutar test
        integration_test = ProductionIntegrationTest(production_path)
        success = integration_test.run_complete_test()
        
        if success:
            output_manager.success("🎉 ¡TEST DE INTEGRACION CON CARPETA DE PRODUCCION COMPLETADO EXITOSAMENTE!")
            sys.exit(0)
        else:
            output_manager.error("❌ TEST DE INTEGRACION CON CARPETA DE PRODUCCION FALLO")
            sys.exit(1)
            
    except Exception as e:
        output_manager.error(f"❌ Error critico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

