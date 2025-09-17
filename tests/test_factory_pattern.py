#!/usr/bin/env python3
"""
Tests para Factory Pattern
=========================

Tests específicos para el patrón Factory implementado en el sistema.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.converters.factory import ConverterFactory, PostConverterFactory
from src.converters.base import BaseConverter
from src.config_manager import ConfigManager


class MockConverter(BaseConverter):
    """Conversor mock para testing"""
    
    def __init__(self, config):
        super().__init__(config)
        self.config = config
    
    def convert(self, input_path, output_path):
        return True
    
    def get_file_extension(self):
        return ".mock"
    
    def get_output_filename(self, input_file, output_dir):
        return output_dir / f"{input_file.stem}.mock"


class MockPostConverter:
    """Postconversor mock para testing"""
    
    def __init__(self, config):
        self.config = config


def test_converter_factory_registration():
    """Test de registro de conversores en el factory"""
    print("🧪 Probando registro de conversores...")
    
    # Limpiar conversores registrados para test limpio
    original_converters = ConverterFactory._converters.copy()
    
    try:
        # Registrar nuevo conversor
        ConverterFactory.register_converter("MOCK", MockConverter)
        
        # Verificar que se registró
        assert "MOCK" in ConverterFactory._converters
        assert ConverterFactory._converters["MOCK"] == MockConverter
        
        print("✅ Registro de conversor exitoso")
        
    finally:
        # Restaurar conversores originales
        ConverterFactory._converters = original_converters


def test_converter_factory_creation():
    """Test de creación de conversores"""
    print("🧪 Probando creación de conversores...")
    
    # Configuración de prueba
    config = {
        'enabled': True,
        'quality': 95,
        'dpi': 300
    }
    
    # Crear conversor
    converter = ConverterFactory.create_converter("JPGHIGH", config)
    
    # Verificar creación
    assert converter is not None
    assert hasattr(converter, 'config')
    assert converter.config['enabled'] is True
    
    print("✅ Creación de conversor exitosa")


def test_converter_factory_invalid_converter():
    """Test de manejo de conversores inválidos"""
    print("🧪 Probando manejo de conversores inválidos...")
    
    # Intentar crear conversor no registrado
    converter = ConverterFactory.create_converter("INVALID", {})
    
    # Debe retornar None
    assert converter is None
    
    print("✅ Manejo de conversor inválido correcto")


def test_converter_factory_invalid_class():
    """Test de registro de clase inválida"""
    print("🧪 Probando registro de clase inválida...")
    
    class InvalidConverter:
        """Clase que no hereda de BaseConverter"""
        pass
    
    try:
        # Debe lanzar ValueError
        ConverterFactory.register_converter("INVALID", InvalidConverter)
        assert False, "Debería haber lanzado ValueError"
    except ValueError as e:
        assert "debe heredar de BaseConverter" in str(e)
        print("✅ Validación de herencia correcta")


def test_converter_factory_available_converters():
    """Test de lista de conversores disponibles"""
    print("🧪 Probando lista de conversores disponibles...")
    
    available = ConverterFactory.get_available_converters()
    
    # Verificar que contiene conversores básicos
    assert "JPGHIGH" in available
    assert "JPGLOW" in available
    assert "PDF" in available
    assert "MET" in available
    
    print(f"✅ Conversores disponibles: {available}")


def test_converter_factory_from_config():
    """Test de creación de conversores desde configuración"""
    print("🧪 Probando creación desde configuración...")
    
    # Crear configuración temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
formats:
  JPGHIGH:
    enabled: true
    quality: 95
    dpi: 400
  JPGLOW:
    enabled: true
    quality: 90
    dpi: 200
  PDF:
    enabled: true
    resolution: 300
  INVALID:
    enabled: true
    invalid_param: "test"
""")
        config_path = f.name
    
    try:
        # Crear config manager
        config_manager = ConfigManager(config_path)
        
        # Crear conversores desde configuración
        converters = ConverterFactory.create_converters_from_config(config_manager)
        
        # Verificar conversores creados
        assert len(converters) >= 3  # Al menos JPGHIGH, JPGLOW, PDF
        assert "JPGHIGH" in converters
        assert "JPGLOW" in converters
        assert "PDF" in converters
        
        # Verificar que cada conversor tiene configuración
        for name, converter in converters.items():
            assert converter is not None
            assert hasattr(converter, 'config')
        
        print(f"✅ Conversores creados desde configuración: {list(converters.keys())}")
        
    finally:
        # Limpiar archivo temporal
        Path(config_path).unlink(missing_ok=True)


def test_postconverter_factory():
    """Test del factory de postconversores"""
    print("🧪 Probando factory de postconversores...")
    
    # Registrar postconversor mock
    PostConverterFactory.register_postconverter("MOCK", MockPostConverter)
    
    # Crear postconversor
    config = {'enabled': True}
    postconverter = PostConverterFactory.create_postconverter("MOCK", config)
    
    # Verificar creación
    assert postconverter is not None
    assert hasattr(postconverter, 'config')
    assert postconverter.config['enabled'] is True
    
    print("✅ Factory de postconversores funcionando")


def test_factory_error_handling():
    """Test de manejo de errores en factory"""
    print("🧪 Probando manejo de errores en factory...")
    
    # Mock de conversor que falla en inicialización
    class FailingConverter(BaseConverter):
        def __init__(self, config):
            raise Exception("Error de inicialización")
        
        def convert(self, input_path, output_path):
            return True
        
        def get_file_extension(self):
            return ".fail"
        
        def get_output_filename(self, input_file, output_dir):
            return output_dir / f"{input_file.stem}.fail"
    
    # Registrar conversor que falla
    ConverterFactory.register_converter("FAILING", FailingConverter)
    
    # Intentar crear conversor que falla
    converter = ConverterFactory.create_converter("FAILING", {})
    
    # Debe retornar None por el error
    assert converter is None
    
    print("✅ Manejo de errores en factory correcto")


def run_factory_tests():
    """Ejecuta todos los tests del Factory Pattern"""
    print("🚀 Iniciando tests del Factory Pattern...")
    print("=" * 50)
    
    tests = [
        test_converter_factory_registration,
        test_converter_factory_creation,
        test_converter_factory_invalid_converter,
        test_converter_factory_invalid_class,
        test_converter_factory_available_converters,
        test_converter_factory_from_config,
        test_postconverter_factory,
        test_factory_error_handling
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
    print(f"📊 Resultados Factory Pattern:")
    print(f"✅ Tests pasados: {passed}")
    print(f"❌ Tests fallidos: {failed}")
    print(f"📈 Tasa de éxito: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🎉 ¡Todos los tests del Factory Pattern pasaron!")
        return True
    else:
        print("⚠️ Algunos tests del Factory Pattern fallaron")
        return False


if __name__ == "__main__":
    success = run_factory_tests()
    sys.exit(0 if success else 1)
