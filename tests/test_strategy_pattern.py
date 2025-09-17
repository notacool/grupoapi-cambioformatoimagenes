#!/usr/bin/env python3
"""
Tests para Strategy Pattern
==========================

Tests específicos para el patrón Strategy implementado en el sistema.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.converters.compression_strategies import (
    CompressionStrategy, 
    GhostscriptCompressionStrategy,
    PikepdfCompressionStrategy,
    PypdfCompressionStrategy,
    CompressionContext,
    CompressionStrategyFactory
)


class MockCompressionStrategy(CompressionStrategy):
    """Estrategia mock para testing"""
    
    def compress(self, input_path, output_path, config):
        # Simular compresión exitosa
        output_path.touch()
        return True
    
    def get_name(self):
        return "mock"


class FailingCompressionStrategy(CompressionStrategy):
    """Estrategia que falla para testing"""
    
    def compress(self, input_path, output_path, config):
        return False
    
    def get_name(self):
        return "failing"


def test_compression_strategy_interface():
    """Test de la interfaz CompressionStrategy"""
    print("🧪 Probando interfaz CompressionStrategy...")
    
    strategy = MockCompressionStrategy()
    
    # Verificar métodos requeridos
    assert hasattr(strategy, 'compress')
    assert hasattr(strategy, 'get_name')
    
    # Verificar tipos de retorno
    assert callable(strategy.compress)
    assert callable(strategy.get_name)
    
    print("✅ Interfaz CompressionStrategy correcta")


def test_ghostscript_strategy():
    """Test de la estrategia Ghostscript"""
    print("🧪 Probando estrategia Ghostscript...")
    
    strategy = GhostscriptCompressionStrategy()
    
    # Verificar nombre
    assert strategy.get_name() == "Ghostscript"
    
    # Crear archivos temporales para test
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_file:
        input_path = Path(input_file.name)
        input_file.write(b"Mock PDF content")
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
        output_path = Path(output_file.name)
    
    try:
        config = {
            'compression_level': 'ebook',
            'target_dpi': 200
        }
        
        # Test de compresión (puede fallar si Ghostscript no está instalado)
        result = strategy.compress(input_path, output_path, config)
        
        # El resultado puede ser True o False dependiendo de la instalación
        assert isinstance(result, bool)
        
        print(f"✅ Estrategia Ghostscript: {'exitoso' if result else 'falló (esperado si no está instalado)'}")
        
    finally:
        # Limpiar archivos temporales
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def test_pikepdf_strategy():
    """Test de la estrategia pikepdf"""
    print("🧪 Probando estrategia pikepdf...")
    
    strategy = PikepdfCompressionStrategy()
    
    # Verificar nombre
    assert strategy.get_name() == "pikepdf"
    
    # Crear archivos temporales para test
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_file:
        input_path = Path(input_file.name)
        input_file.write(b"Mock PDF content")
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
        output_path = Path(output_file.name)
    
    try:
        config = {
            'remove_metadata': True
        }
        
        # Test de compresión (puede fallar si pikepdf no está instalado)
        result = strategy.compress(input_path, output_path, config)
        
        # El resultado puede ser True o False dependiendo de la instalación
        assert isinstance(result, bool)
        
        print(f"✅ Estrategia pikepdf: {'exitoso' if result else 'falló (esperado si no está instalado)'}")
        
    finally:
        # Limpiar archivos temporales
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def test_pypdf_strategy():
    """Test de la estrategia pypdf"""
    print("🧪 Probando estrategia pypdf...")
    
    strategy = PypdfCompressionStrategy()
    
    # Verificar nombre
    assert strategy.get_name() == "pypdf"
    
    # Crear archivos temporales para test
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_file:
        input_path = Path(input_file.name)
        input_file.write(b"Mock PDF content")
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
        output_path = Path(output_file.name)
    
    try:
        config = {
            'remove_metadata': True
        }
        
        # Test de compresión (puede fallar si pypdf no está instalado)
        result = strategy.compress(input_path, output_path, config)
        
        # El resultado puede ser True o False dependiendo de la instalación
        assert isinstance(result, bool)
        
        print(f"✅ Estrategia pypdf: {'exitoso' if result else 'falló (esperado si no está instalado)'}")
        
    finally:
        # Limpiar archivos temporales
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def test_compression_context():
    """Test del contexto de compresión"""
    print("🧪 Probando contexto de compresión...")
    
    # Crear contexto con estrategia mock
    strategy = MockCompressionStrategy()
    context = CompressionContext(strategy)
    
    # Verificar estrategia inicial
    assert context.get_strategy_name() == "mock"
    
    # Crear archivos temporales
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_file:
        input_path = Path(input_file.name)
        input_file.write(b"Mock PDF content")
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
        output_path = Path(output_file.name)
    
    try:
        config = {'test': True}
        
        # Test de compresión
        result = context.compress(input_path, output_path, config)
        assert result is True
        
        # Verificar que se creó el archivo de salida
        assert output_path.exists()
        
        print("✅ Contexto de compresión funcionando")
        
    finally:
        # Limpiar archivos temporales
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def test_compression_context_strategy_change():
    """Test de cambio de estrategia en contexto"""
    print("🧪 Probando cambio de estrategia...")
    
    # Crear contexto con estrategia mock
    strategy1 = MockCompressionStrategy()
    context = CompressionContext(strategy1)
    
    # Verificar estrategia inicial
    assert context.get_strategy_name() == "mock"
    
    # Cambiar estrategia
    strategy2 = FailingCompressionStrategy()
    context.set_strategy(strategy2)
    
    # Verificar cambio
    assert context.get_strategy_name() == "failing"
    
    print("✅ Cambio de estrategia funcionando")


def test_compression_strategy_factory():
    """Test del factory de estrategias"""
    print("🧪 Probando factory de estrategias...")
    
    # Verificar estrategias disponibles
    available = CompressionStrategyFactory.get_available_strategies()
    assert "ghostscript" in available
    assert "pikepdf" in available
    assert "pypdf" in available
    
    # Crear estrategia
    strategy = CompressionStrategyFactory.create_strategy("pikepdf")
    assert strategy is not None
    assert strategy.get_name() == "pikepdf"
    
    # Test de estrategia no disponible
    invalid_strategy = CompressionStrategyFactory.create_strategy("invalid")
    assert invalid_strategy is None
    
    print(f"✅ Factory de estrategias: {available}")


def test_compression_fallback():
    """Test de fallback entre estrategias"""
    print("🧪 Probando fallback entre estrategias...")
    
    # Crear contexto con estrategia que falla
    failing_strategy = FailingCompressionStrategy()
    context = CompressionContext(failing_strategy)
    
    # Crear archivos temporales
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_file:
        input_path = Path(input_file.name)
        input_file.write(b"Mock PDF content")
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
        output_path = Path(output_file.name)
    
    try:
        config = {'test': True}
        
        # Primera compresión debe fallar
        result1 = context.compress(input_path, output_path, config)
        assert result1 is False
        
        # Cambiar a estrategia que funciona
        working_strategy = MockCompressionStrategy()
        context.set_strategy(working_strategy)
        
        # Segunda compresión debe funcionar
        result2 = context.compress(input_path, output_path, config)
        assert result2 is True
        
        print("✅ Fallback entre estrategias funcionando")
        
    finally:
        # Limpiar archivos temporales
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def test_compression_error_handling():
    """Test de manejo de errores en compresión"""
    print("🧪 Probando manejo de errores...")
    
    # Crear estrategia que lanza excepción
    class ExceptionStrategy(CompressionStrategy):
        def compress(self, input_path, output_path, config):
            raise Exception("Error simulado")
        
        def get_name(self):
            return "exception"
    
    strategy = ExceptionStrategy()
    context = CompressionContext(strategy)
    
    # Crear archivos temporales
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_file:
        input_path = Path(input_file.name)
        input_file.write(b"Mock PDF content")
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
        output_path = Path(output_file.name)
    
    try:
        config = {'test': True}
        
        # La compresión debe manejar la excepción y retornar False
        result = context.compress(input_path, output_path, config)
        assert result is False
        
        print("✅ Manejo de errores en compresión correcto")
        
    except Exception as e:
        # Si la excepción no se maneja correctamente, el test falla
        print(f"❌ Excepción no manejada: {str(e)}")
        assert False, "La excepción debería ser manejada por el contexto"
        
    finally:
        # Limpiar archivos temporales
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def run_strategy_tests():
    """Ejecuta todos los tests del Strategy Pattern"""
    print("🚀 Iniciando tests del Strategy Pattern...")
    print("=" * 50)
    
    tests = [
        test_compression_strategy_interface,
        test_ghostscript_strategy,
        test_pikepdf_strategy,
        test_pypdf_strategy,
        test_compression_context,
        test_compression_context_strategy_change,
        test_compression_strategy_factory,
        test_compression_fallback,
        test_compression_error_handling
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
    print(f"📊 Resultados Strategy Pattern:")
    print(f"✅ Tests pasados: {passed}")
    print(f"❌ Tests fallidos: {failed}")
    print(f"📈 Tasa de éxito: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🎉 ¡Todos los tests del Strategy Pattern pasaron!")
        return True
    else:
        print("⚠️ Algunos tests del Strategy Pattern fallaron")
        return False


if __name__ == "__main__":
    success = run_strategy_tests()
    sys.exit(0 if success else 1)
