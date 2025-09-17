#!/usr/bin/env python3
"""
Tests para Builder Pattern
=========================

Tests específicos para el patrón Builder implementado en el sistema.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config_builder import (
    ConfigBuilder, ProductionConfigBuilder, DevelopmentConfigBuilder
)


def test_config_builder_basic():
    """Test básico del ConfigBuilder"""
    print("🧪 Probando ConfigBuilder básico...")
    
    builder = ConfigBuilder()
    
    # Construir configuración básica
    config = (builder
              .add_format("JPGHIGH")
              .set_format_enabled(True)
              .set_format_quality(95)
              .set_format_dpi(400)
              .build())
    
    # Verificar estructura
    assert "formats" in config
    assert "JPGHIGH" in config["formats"]
    assert config["formats"]["JPGHIGH"]["enabled"] is True
    assert config["formats"]["JPGHIGH"]["quality"] == 95
    assert config["formats"]["JPGHIGH"]["dpi"] == 400
    
    print("✅ ConfigBuilder básico funcionando")


def test_config_builder_validation():
    """Test de validación del ConfigBuilder"""
    print("🧪 Probando validación del ConfigBuilder...")
    
    builder = ConfigBuilder()
    
    # Configuración válida
    valid_config = (builder
                    .add_format("JPGHIGH")
                    .set_format_enabled(True)
                    .set_format_quality(95)
                    .build())
    
    assert builder.validate() is True
    
    # Configuración inválida (calidad fuera de rango)
    builder2 = ConfigBuilder()
    builder2.add_format("JPGHIGH")
    builder2.set_format_quality(150)  # Fuera de rango 1-100
    
    # La validación debe fallar
    assert builder2.validate() is False
    
    print("✅ Validación del ConfigBuilder funcionando")


def test_config_builder_pdf_config():
    """Test de configuración específica de PDF"""
    print("🧪 Probando configuración de PDF...")
    
    builder = ConfigBuilder()
    
    config = (builder
              .add_format("PDF")
              .add_pdf_config(resolution=300, page_size="A4")
              .build())
    
    # Verificar configuración PDF
    pdf_config = config["formats"]["PDF"]
    assert pdf_config["resolution"] == 300
    assert pdf_config["page_size"] == "A4"
    assert pdf_config["fit_to_page"] is True
    assert pdf_config["ocr_language"] == ["es", "en"]
    assert pdf_config["ocr_confidence"] == 0.2
    assert pdf_config["create_searchable_pdf"] is True
    
    print("✅ Configuración de PDF funcionando")


def test_config_builder_postconverter():
    """Test de configuración de postconversores"""
    print("🧪 Probando configuración de postconversores...")
    
    builder = ConfigBuilder()
    
    config = (builder
              .add_postconverter("consolidated_pdf")
              .set_postconverter_enabled(True)
              .set_pdf_max_size(5000)
              .add_compression_config(level="ebook", target_dpi=200)
              .build())
    
    # Verificar configuración de postconversor
    assert "postconverters" in config
    assert "consolidated_pdf" in config["postconverters"]
    
    pdf_config = config["postconverters"]["consolidated_pdf"]
    assert pdf_config["enabled"] is True
    assert pdf_config["max_size_mb"] == 5000
    
    # Verificar configuración de compresión
    assert "compression" in pdf_config
    compression = pdf_config["compression"]
    assert compression["enabled"] is True
    assert compression["compression_level"] == "ebook"
    assert compression["target_dpi"] == 200
    assert compression["image_quality"] == 85
    assert compression["remove_metadata"] is True
    
    print("✅ Configuración de postconversores funcionando")


def test_config_builder_metadata():
    """Test de configuración de metadatos"""
    print("🧪 Probando configuración de metadatos...")
    
    builder = ConfigBuilder()
    
    config = (builder
              .add_metadata_config("Mi Organización", "Mi Sistema")
              .build())
    
    # Verificar configuración de metadatos
    assert "metadata" in config
    metadata = config["metadata"]
    assert metadata["organization"] == "Mi Organización"
    assert metadata["creator"] == "Mi Sistema"
    assert metadata["generate_all_met"] is False
    
    print("✅ Configuración de metadatos funcionando")


def test_config_builder_system():
    """Test de configuración del sistema"""
    print("🧪 Probando configuración del sistema...")
    
    builder = ConfigBuilder()
    
    config = (builder
              .add_system_config(max_workers=4, log_level="DEBUG")
              .build())
    
    # Verificar configuración del sistema
    assert "system" in config
    system = config["system"]
    assert system["max_workers"] == 4
    assert system["log_level"] == "DEBUG"
    assert system["temp_dir"] is None
    
    print("✅ Configuración del sistema funcionando")


def test_config_builder_save_to_file():
    """Test de guardado en archivo"""
    print("🧪 Probando guardado en archivo...")
    
    builder = ConfigBuilder()
    
    config = (builder
              .add_format("JPGHIGH")
              .set_format_quality(95)
              .add_metadata_config("Test Org", "Test System")
              .build())
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        temp_file = f.name
    
    try:
        # Guardar configuración
        success = builder.save_to_file(temp_file)
        assert success is True
        
        # Verificar que el archivo existe
        assert Path(temp_file).exists()
        
        # Verificar contenido del archivo
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "JPGHIGH" in content
            assert "quality: 95" in content
            assert "Test Org" in content
        
        print("✅ Guardado en archivo funcionando")
        
    finally:
        # Limpiar archivo temporal
        Path(temp_file).unlink(missing_ok=True)


def test_production_config_builder():
    """Test del ProductionConfigBuilder"""
    print("🧪 Probando ProductionConfigBuilder...")
    
    builder = ProductionConfigBuilder()
    config = builder.build_production_config()
    
    # Verificar formatos de producción
    assert "formats" in config
    assert "JPGHIGH" in config["formats"]
    assert "JPGLOW" in config["formats"]
    assert "PDF" in config["formats"]
    
    # Verificar configuración JPGHIGH
    jpghigh = config["formats"]["JPGHIGH"]
    assert jpghigh["enabled"] is True
    assert jpghigh["quality"] == 95
    assert jpghigh["dpi"] == 400
    assert jpghigh["optimize"] is True
    
    # Verificar configuración JPGLOW
    jpglow = config["formats"]["JPGLOW"]
    assert jpglow["enabled"] is True
    assert jpglow["quality"] == 90
    assert jpglow["dpi"] == 200
    assert jpglow["optimize"] is True
    
    # Verificar configuración PDF
    pdf = config["formats"]["PDF"]
    assert pdf["enabled"] is True
    assert pdf["resolution"] == 300
    assert pdf["page_size"] == "A4"
    
    # Verificar postconversores
    assert "postconverters" in config
    assert "consolidated_pdf" in config["postconverters"]
    assert "met_format" in config["postconverters"]
    
    # Verificar configuración de PDF consolidado
    consolidated_pdf = config["postconverters"]["consolidated_pdf"]
    assert consolidated_pdf["enabled"] is True
    assert consolidated_pdf["max_size_mb"] == 5000
    
    # Verificar metadatos
    assert "metadata" in config
    assert config["metadata"]["organization"] == "Grupo API"
    assert config["metadata"]["creator"] == "Sistema Automatizado"
    
    # Verificar sistema
    assert "system" in config
    assert config["system"]["max_workers"] == 4
    assert config["system"]["log_level"] == "INFO"
    
    print("✅ ProductionConfigBuilder funcionando")


def test_development_config_builder():
    """Test del DevelopmentConfigBuilder"""
    print("🧪 Probando DevelopmentConfigBuilder...")
    
    builder = DevelopmentConfigBuilder()
    config = builder.build_development_config()
    
    # Verificar formatos de desarrollo
    assert "formats" in config
    assert "JPGHIGH" in config["formats"]
    assert "PDF" in config["formats"]
    
    # Verificar configuración JPGHIGH (desarrollo)
    jpghigh = config["formats"]["JPGHIGH"]
    assert jpghigh["enabled"] is True
    assert jpghigh["quality"] == 85  # Menor calidad para desarrollo
    assert jpghigh["dpi"] == 300     # Menor DPI para desarrollo
    assert jpghigh["optimize"] is False  # Sin optimización para desarrollo
    
    # Verificar configuración PDF (desarrollo)
    pdf = config["formats"]["PDF"]
    assert pdf["enabled"] is True
    assert pdf["resolution"] == 200  # Menor resolución para desarrollo
    assert pdf["page_size"] == "A4"
    
    # Verificar postconversores (desarrollo)
    assert "postconverters" in config
    assert "consolidated_pdf" in config["postconverters"]
    
    # Verificar configuración de PDF consolidado (desarrollo)
    consolidated_pdf = config["postconverters"]["consolidated_pdf"]
    assert consolidated_pdf["enabled"] is True
    assert consolidated_pdf["max_size_mb"] == 100  # Menor tamaño para desarrollo
    
    # Verificar configuración de compresión (desarrollo)
    compression = consolidated_pdf["compression"]
    assert compression["compression_level"] == "screen"  # Compresión más agresiva
    assert compression["target_dpi"] == 150  # Menor DPI
    
    # Verificar metadatos (desarrollo)
    assert "metadata" in config
    assert config["metadata"]["organization"] == "Desarrollo"
    assert config["metadata"]["creator"] == "Sistema de Pruebas"
    
    # Verificar sistema (desarrollo)
    assert "system" in config
    assert config["system"]["max_workers"] == 2  # Menos workers para desarrollo
    assert config["system"]["log_level"] == "DEBUG"  # Más logging para desarrollo
    
    print("✅ DevelopmentConfigBuilder funcionando")


def test_config_builder_method_chaining():
    """Test de method chaining"""
    print("🧪 Probando method chaining...")
    
    builder = ConfigBuilder()
    
    # Verificar que todos los métodos retornan self
    result = (builder
              .add_format("JPGHIGH")
              .set_format_enabled(True)
              .set_format_quality(95)
              .set_format_dpi(400)
              .set_format_optimize(True)
              .add_pdf_config(300, "A4")
              .add_postconverter("consolidated_pdf")
              .set_postconverter_enabled(True)
              .set_pdf_max_size(5000)
              .add_compression_config("ebook", 200)
              .add_metadata_config("Test Org", "Test System")
              .add_system_config(4, "INFO"))
    
    # Verificar que retorna el builder
    assert result is builder
    
    # Verificar que se puede construir
    config = builder.build()
    assert config is not None
    
    print("✅ Method chaining funcionando")


def test_config_builder_error_handling():
    """Test de manejo de errores"""
    print("🧪 Probando manejo de errores...")
    
    builder = ConfigBuilder()
    
    # Test de configuración inválida
    builder2 = ConfigBuilder()
    builder2.add_format("JPGHIGH")
    builder2.set_format_quality(150)  # Inválido
    
    # La validación debe fallar
    assert builder2.validate() is False
    print("✅ Validación de calidad correcta")
    
    # Test de guardado en archivo con error
    builder2 = ConfigBuilder()
    config = builder2.add_format("JPGHIGH").build()
    
    # Intentar guardar en ruta inválida
    success = builder2.save_to_file("/ruta/invalida/config.yaml")
    assert success is False
    
    print("✅ Manejo de errores funcionando")


def run_builder_tests():
    """Ejecuta todos los tests del Builder Pattern"""
    print("🚀 Iniciando tests del Builder Pattern...")
    print("=" * 50)
    
    tests = [
        test_config_builder_basic,
        test_config_builder_validation,
        test_config_builder_pdf_config,
        test_config_builder_postconverter,
        test_config_builder_metadata,
        test_config_builder_system,
        test_config_builder_save_to_file,
        test_production_config_builder,
        test_development_config_builder,
        test_config_builder_method_chaining,
        test_config_builder_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test falló: {test.__name__} - {str(e)}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Resultados Builder Pattern:")
    print(f"✅ Tests pasados: {passed}")
    print(f"❌ Tests fallidos: {failed}")
    print(f"📈 Tasa de éxito: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🎉 ¡Todos los tests del Builder Pattern pasaron!")
        return True
    else:
        print("⚠️ Algunos tests del Builder Pattern fallaron")
        return False


if __name__ == "__main__":
    success = run_builder_tests()
    sys.exit(0 if success else 1)
