#!/usr/bin/env python3
"""
Tests para Command Pattern
=========================

Tests específicos para el patrón Command implementado en el sistema.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.commands.command_pattern import (
    Command, ConvertFileCommand, CreateDirectoryCommand, 
    DeleteFileCommand, CommandInvoker, MacroCommand
)


class MockCommand(Command):
    """Comando mock para testing"""
    
    def __init__(self, should_succeed=True):
        self.should_succeed = should_succeed
        self.executed = False
        self.undone = False
    
    def execute(self) -> bool:
        self.executed = True
        return self.should_succeed
    
    def undo(self) -> bool:
        self.undone = True
        return True
    
    def get_description(self) -> str:
        return "Mock Command"


class FailingCommand(Command):
    """Comando que falla para testing"""
    
    def __init__(self):
        self.executed = False
        self.undone = False
    
    def execute(self) -> bool:
        self.executed = True
        return False
    
    def undo(self) -> bool:
        self.undone = True
        return True
    
    def get_description(self) -> str:
        return "Failing Command"


class FailingUndoCommand(Command):
    """Comando que falla al deshacer"""
    
    def execute(self) -> bool:
        return True
    
    def undo(self) -> bool:
        return False
    
    def get_description(self) -> str:
        return "Failing Undo Command"


def test_command_interface():
    """Test de la interfaz Command"""
    print("🧪 Probando interfaz Command...")
    
    command = MockCommand()
    
    # Verificar métodos requeridos
    assert hasattr(command, 'execute')
    assert hasattr(command, 'undo')
    assert hasattr(command, 'get_description')
    
    # Verificar tipos de retorno
    assert callable(command.execute)
    assert callable(command.undo)
    assert callable(command.get_description)
    
    # Verificar descripción
    description = command.get_description()
    assert isinstance(description, str)
    assert description == "Mock Command"
    
    print("✅ Interfaz Command correcta")


def test_convert_file_command():
    """Test del ConvertFileCommand"""
    print("🧪 Probando ConvertFileCommand...")
    
    # Crear archivos temporales
    with tempfile.NamedTemporaryFile(suffix='.tiff', delete=False) as input_file:
        input_path = Path(input_file.name)
        input_file.write(b"Mock TIFF content")
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
        output_path = Path(output_file.name)
    
    try:
        # Crear conversor mock
        mock_converter = Mock()
        mock_converter.convert.return_value = True
        
        # Crear comando
        command = ConvertFileCommand(mock_converter, input_path, output_path, "PDF")
        
        # Verificar descripción
        description = command.get_description()
        assert "Convertir" in description
        assert "PDF" in description
        
        # Ejecutar comando
        result = command.execute()
        assert result is True
        
        # Verificar que se llamó al conversor
        mock_converter.convert.assert_called_once_with(input_path, output_path)
        
        # Verificar que se creó backup
        assert command.original_file_exists is False  # No había archivo original
        
        # Deshacer comando
        undo_result = command.undo()
        assert undo_result is True
        
        print("✅ ConvertFileCommand funcionando")
        
    finally:
        # Limpiar archivos temporales
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def test_create_directory_command():
    """Test del CreateDirectoryCommand"""
    print("🧪 Probando CreateDirectoryCommand...")
    
    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as temp_dir:
        directory_path = Path(temp_dir) / "test_subdir"
        
        # Crear comando
        command = CreateDirectoryCommand(directory_path)
        
        # Verificar descripción
        description = command.get_description()
        assert "Crear directorio" in description
        assert "test_subdir" in description
        
        # Ejecutar comando
        result = command.execute()
        assert result is True
        assert directory_path.exists()
        assert directory_path.is_dir()
        
        # Deshacer comando
        undo_result = command.undo()
        assert undo_result is True
        assert not directory_path.exists()


def test_create_directory_command_existing():
    """Test del CreateDirectoryCommand con directorio existente"""
    print("🧪 Probando CreateDirectoryCommand con directorio existente...")
    
    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as temp_dir:
        directory_path = Path(temp_dir) / "existing_dir"
        directory_path.mkdir()  # Crear directorio existente
        
        # Crear comando
        command = CreateDirectoryCommand(directory_path)
        
        # Ejecutar comando (debe funcionar aunque ya existe)
        result = command.execute()
        assert result is True
        assert directory_path.exists()
        
        # Deshacer comando (no debe eliminar porque ya existía)
        undo_result = command.undo()
        assert undo_result is True
        assert directory_path.exists()  # Debe seguir existiendo


def test_delete_file_command():
    """Test del DeleteFileCommand"""
    print("🧪 Probando DeleteFileCommand...")
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        file_path = Path(temp_file.name)
        temp_file.write(b"Test content")
    
    try:
        # Crear comando
        command = DeleteFileCommand(file_path)
        
        # Verificar descripción
        description = command.get_description()
        assert "Eliminar archivo" in description
        assert file_path.name in description
        
        # Ejecutar comando
        result = command.execute()
        assert result is True
        assert not file_path.exists()  # Archivo eliminado
        assert command.backup_path.exists()  # Backup creado
        
        # Deshacer comando
        undo_result = command.undo()
        assert undo_result is True
        assert file_path.exists()  # Archivo restaurado
        assert not command.backup_path.exists()  # Backup eliminado
        
    finally:
        # Limpiar archivos temporales
        file_path.unlink(missing_ok=True)
        if hasattr(command, 'backup_path') and command.backup_path:
            command.backup_path.unlink(missing_ok=True)


def test_delete_file_command_nonexistent():
    """Test del DeleteFileCommand con archivo inexistente"""
    print("🧪 Probando DeleteFileCommand con archivo inexistente...")
    
    # Crear comando para archivo que no existe
    nonexistent_path = Path("nonexistent_file.txt")
    command = DeleteFileCommand(nonexistent_path)
    
    # Ejecutar comando (debe funcionar aunque no existe)
    result = command.execute()
    assert result is True
    
    # Deshacer comando
    undo_result = command.undo()
    assert undo_result is True


def test_command_invoker():
    """Test del CommandInvoker"""
    print("🧪 Probando CommandInvoker...")
    
    invoker = CommandInvoker()
    
    # Verificar estado inicial
    assert len(invoker.history) == 0
    assert len(invoker.undo_history) == 0
    
    # Crear comando
    command = MockCommand()
    
    # Ejecutar comando
    result = invoker.execute_command(command)
    assert result is True
    assert len(invoker.history) == 1
    assert command.executed is True
    
    # Verificar historial
    history = invoker.get_history()
    assert len(history) == 1
    assert history[0] is command
    
    print("✅ CommandInvoker funcionando")


def test_command_invoker_undo_redo():
    """Test de deshacer/rehacer comandos"""
    print("🧪 Probando deshacer/rehacer comandos...")
    
    invoker = CommandInvoker()
    
    # Crear comandos
    command1 = MockCommand()
    command2 = MockCommand()
    
    # Ejecutar comandos
    invoker.execute_command(command1)
    invoker.execute_command(command2)
    
    assert len(invoker.history) == 2
    assert len(invoker.undo_history) == 0
    
    # Deshacer último comando
    undo_result = invoker.undo_last_command()
    assert undo_result is True
    assert len(invoker.history) == 1
    assert len(invoker.undo_history) == 1
    assert command2.undone is True
    
    # Rehacer comando
    redo_result = invoker.redo_last_command()
    assert redo_result is True
    assert len(invoker.history) == 2
    assert len(invoker.undo_history) == 0
    assert command2.executed is True  # Se ejecutó de nuevo
    
    print("✅ Deshacer/rehacer comandos funcionando")


def test_command_invoker_undo_empty():
    """Test de deshacer con historial vacío"""
    print("🧪 Probando deshacer con historial vacío...")
    
    invoker = CommandInvoker()
    
    # Intentar deshacer sin comandos
    result = invoker.undo_last_command()
    assert result is False
    
    print("✅ Deshacer con historial vacío correcto")


def test_command_invoker_redo_empty():
    """Test de rehacer con historial vacío"""
    print("🧪 Probando rehacer con historial vacío...")
    
    invoker = CommandInvoker()
    
    # Intentar rehacer sin comandos
    result = invoker.redo_last_command()
    assert result is False
    
    print("✅ Rehacer con historial vacío correcto")


def test_command_invoker_failing_command():
    """Test de comando que falla"""
    print("🧪 Probando comando que falla...")
    
    invoker = CommandInvoker()
    
    # Crear comando que falla
    failing_command = FailingCommand()
    
    # Ejecutar comando que falla
    result = invoker.execute_command(failing_command)
    assert result is False
    assert len(invoker.history) == 0  # No se agrega al historial
    
    print("✅ Comando que falla manejado correctamente")


def test_command_invoker_failing_undo():
    """Test de comando que falla al deshacer"""
    print("🧪 Probando comando que falla al deshacer...")
    
    invoker = CommandInvoker()
    
    # Crear comando que falla al deshacer
    failing_undo_command = FailingUndoCommand()
    
    # Ejecutar comando
    result = invoker.execute_command(failing_undo_command)
    assert result is True
    assert len(invoker.history) == 1
    
    # Intentar deshacer (debe fallar)
    undo_result = invoker.undo_last_command()
    assert undo_result is False
    assert len(invoker.history) == 1  # Comando se mantiene en historial
    
    print("✅ Comando que falla al deshacer manejado correctamente")


def test_macro_command():
    """Test del MacroCommand"""
    print("🧪 Probando MacroCommand...")
    
    # Crear comandos
    command1 = MockCommand()
    command2 = MockCommand()
    command3 = MockCommand()
    
    commands = [command1, command2, command3]
    macro = MacroCommand(commands, "Test Macro")
    
    # Verificar descripción
    description = macro.get_description()
    assert description == "Test Macro"
    
    # Ejecutar macro
    result = macro.execute()
    assert result is True
    
    # Verificar que todos los comandos se ejecutaron
    assert command1.executed is True
    assert command2.executed is True
    assert command3.executed is True
    
    # Deshacer macro
    undo_result = macro.undo()
    assert undo_result is True
    
    # Verificar que todos los comandos se deshicieron
    assert command1.undone is True
    assert command2.undone is True
    assert command3.undone is True
    
    print("✅ MacroCommand funcionando")


def test_macro_command_failing():
    """Test de MacroCommand que falla"""
    print("🧪 Probando MacroCommand que falla...")
    
    # Crear comandos (uno que falla)
    command1 = MockCommand()
    command2 = FailingCommand()
    command3 = MockCommand()
    
    commands = [command1, command2, command3]
    macro = MacroCommand(commands, "Failing Macro")
    
    # Ejecutar macro (debe fallar)
    result = macro.execute()
    assert result is False
    
    # Verificar que solo se ejecutaron los comandos hasta el que falló
    assert command1.executed is True
    assert command2.executed is True
    assert command3.executed is False  # No se ejecutó
    
    # Verificar que se deshicieron los comandos ejecutados
    assert command1.undone is True
    assert command2.undone is False  # No se deshizo porque falló
    
    print("✅ MacroCommand que falla manejado correctamente")


def test_command_invoker_max_history():
    """Test del límite de historial"""
    print("🧪 Probando límite de historial...")
    
    invoker = CommandInvoker()
    invoker.max_history = 3  # Límite pequeño para test
    
    # Ejecutar más comandos que el límite
    commands = [MockCommand() for _ in range(5)]
    for command in commands:
        invoker.execute_command(command)
    
    # Verificar que solo se mantienen los últimos 3
    assert len(invoker.history) == 3
    
    # Verificar que son los últimos 3
    history = invoker.get_history()
    assert history[0] is commands[2]  # Tercer comando
    assert history[1] is commands[3]  # Cuarto comando
    assert history[2] is commands[4]  # Quinto comando
    
    print("✅ Límite de historial funcionando")


def test_command_invoker_clear_history():
    """Test de limpiar historial"""
    print("🧪 Probando limpiar historial...")
    
    invoker = CommandInvoker()
    
    # Ejecutar algunos comandos
    command1 = MockCommand()
    command2 = MockCommand()
    invoker.execute_command(command1)
    invoker.execute_command(command2)
    
    # Deshacer uno
    invoker.undo_last_command()
    
    # Verificar historial
    assert len(invoker.history) == 1
    assert len(invoker.undo_history) == 1
    
    # Limpiar historial
    invoker.clear_history()
    
    # Verificar que se limpió
    assert len(invoker.history) == 0
    assert len(invoker.undo_history) == 0
    
    print("✅ Limpiar historial funcionando")


def test_command_invoker_summary():
    """Test de resumen del historial"""
    print("🧪 Probando resumen del historial...")
    
    invoker = CommandInvoker()
    
    # Estado inicial
    summary = invoker.get_history_summary()
    assert summary['total_commands'] == 0
    assert summary['undo_available'] == 0
    assert summary['last_command'] is None
    
    # Ejecutar comando
    command = MockCommand()
    invoker.execute_command(command)
    
    # Verificar resumen
    summary = invoker.get_history_summary()
    assert summary['total_commands'] == 1
    assert summary['undo_available'] == 0
    assert summary['last_command'] == "Mock Command"
    
    # Deshacer comando
    invoker.undo_last_command()
    
    # Verificar resumen actualizado
    summary = invoker.get_history_summary()
    assert summary['total_commands'] == 0
    assert summary['undo_available'] == 1
    assert summary['last_command'] is None
    
    print("✅ Resumen del historial funcionando")


def run_command_tests():
    """Ejecuta todos los tests del Command Pattern"""
    print("🚀 Iniciando tests del Command Pattern...")
    print("=" * 50)
    
    tests = [
        test_command_interface,
        test_convert_file_command,
        test_create_directory_command,
        test_create_directory_command_existing,
        test_delete_file_command,
        test_delete_file_command_nonexistent,
        test_command_invoker,
        test_command_invoker_undo_redo,
        test_command_invoker_undo_empty,
        test_command_invoker_redo_empty,
        test_command_invoker_failing_command,
        test_command_invoker_failing_undo,
        test_macro_command,
        test_macro_command_failing,
        test_command_invoker_max_history,
        test_command_invoker_clear_history,
        test_command_invoker_summary
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
    print(f"📊 Resultados Command Pattern:")
    print(f"✅ Tests pasados: {passed}")
    print(f"❌ Tests fallidos: {failed}")
    print(f"📈 Tasa de éxito: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🎉 ¡Todos los tests del Command Pattern pasaron!")
        return True
    else:
        print("⚠️ Algunos tests del Command Pattern fallaron")
        return False


if __name__ == "__main__":
    success = run_command_tests()
    sys.exit(0 if success else 1)
