"""
Command Pattern para Operaciones del Sistema
===========================================

Este módulo implementa el patrón Command para encapsular
operaciones del sistema y permitir deshacer/rehacer.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from ..output_manager import output_manager


class Command(ABC):
    """
    Interfaz abstracta para comandos del sistema.
    """
    
    @abstractmethod
    def execute(self) -> bool:
        """
        Ejecuta el comando.
        
        Returns:
            True si la ejecución fue exitosa
        """
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """
        Deshace el comando.
        
        Returns:
            True si el deshacer fue exitoso
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Retorna la descripción del comando.
        
        Returns:
            Descripción del comando
        """
        pass


class ConvertFileCommand(Command):
    """
    Comando para convertir un archivo.
    """
    
    def __init__(self, converter, input_path: Path, output_path: Path, format_name: str):
        """
        Inicializa el comando de conversión.
        
        Args:
            converter: Conversor a utilizar
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            format_name: Nombre del formato
        """
        self.converter = converter
        self.input_path = input_path
        self.output_path = output_path
        self.format_name = format_name
        self.original_file_exists = False
        self.backup_path = None
    
    def execute(self) -> bool:
        """Ejecuta la conversión."""
        try:
            # Crear backup si el archivo de salida existe
            if self.output_path.exists():
                self.original_file_exists = True
                self.backup_path = self.output_path.with_suffix(f"{self.output_path.suffix}.backup")
                self.output_path.rename(self.backup_path)
            
            # Ejecutar conversión
            result = self.converter.convert(self.input_path, self.output_path)
            
            if result:
                output_manager.success(f"✅ Comando ejecutado: {self.get_description()}")
                return True
            else:
                # Restaurar backup si la conversión falló
                if self.original_file_exists and self.backup_path:
                    self.backup_path.rename(self.output_path)
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error ejecutando comando: {str(e)}")
            return False
    
    def undo(self) -> bool:
        """Deshace la conversión."""
        try:
            if self.output_path.exists():
                self.output_path.unlink()
            
            # Restaurar archivo original si existía
            if self.original_file_exists and self.backup_path and self.backup_path.exists():
                self.backup_path.rename(self.output_path)
                output_manager.info(f"↩️ Comando deshecho: {self.get_description()}")
                return True
            
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error deshaciendo comando: {str(e)}")
            return False
    
    def get_description(self) -> str:
        """Retorna la descripción del comando."""
        return f"Convertir {self.input_path.name} a {self.format_name}"


class CreateDirectoryCommand(Command):
    """
    Comando para crear un directorio.
    """
    
    def __init__(self, directory_path: Path):
        """
        Inicializa el comando de creación de directorio.
        
        Args:
            directory_path: Ruta del directorio a crear
        """
        self.directory_path = directory_path
        self.directory_existed = False
    
    def execute(self) -> bool:
        """Ejecuta la creación del directorio."""
        try:
            if self.directory_path.exists():
                self.directory_existed = True
                return True
            
            self.directory_path.mkdir(parents=True, exist_ok=True)
            output_manager.success(f"✅ Directorio creado: {self.directory_path}")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error creando directorio: {str(e)}")
            return False
    
    def undo(self) -> bool:
        """Deshace la creación del directorio."""
        try:
            if not self.directory_existed and self.directory_path.exists():
                self.directory_path.rmdir()
                output_manager.info(f"↩️ Directorio eliminado: {self.directory_path}")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error deshaciendo creación de directorio: {str(e)}")
            return False
    
    def get_description(self) -> str:
        """Retorna la descripción del comando."""
        return f"Crear directorio {self.directory_path.name}"


class DeleteFileCommand(Command):
    """
    Comando para eliminar un archivo.
    """
    
    def __init__(self, file_path: Path):
        """
        Inicializa el comando de eliminación de archivo.
        
        Args:
            file_path: Ruta del archivo a eliminar
        """
        self.file_path = file_path
        self.backup_path = None
        self.file_existed = False
    
    def execute(self) -> bool:
        """Ejecuta la eliminación del archivo."""
        try:
            if not self.file_path.exists():
                return True
            
            self.file_existed = True
            # Crear backup
            self.backup_path = self.file_path.with_suffix(f"{self.file_path.suffix}.deleted")
            self.file_path.rename(self.backup_path)
            
            output_manager.success(f"✅ Archivo eliminado: {self.file_path.name}")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error eliminando archivo: {str(e)}")
            return False
    
    def undo(self) -> bool:
        """Deshace la eliminación del archivo."""
        try:
            if self.file_existed and self.backup_path and self.backup_path.exists():
                self.backup_path.rename(self.file_path)
                output_manager.info(f"↩️ Archivo restaurado: {self.file_path.name}")
                return True
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error deshaciendo eliminación: {str(e)}")
            return False
    
    def get_description(self) -> str:
        """Retorna la descripción del comando."""
        return f"Eliminar archivo {self.file_path.name}"


class CommandInvoker:
    """
    Invocador que ejecuta comandos y mantiene historial.
    """
    
    def __init__(self):
        """Inicializa el invocador."""
        self.history: List[Command] = []
        self.undo_history: List[Command] = []
        self.max_history = 100
    
    def execute_command(self, command: Command) -> bool:
        """
        Ejecuta un comando.
        
        Args:
            command: Comando a ejecutar
            
        Returns:
            True si la ejecución fue exitosa
        """
        try:
            if command.execute():
                self.history.append(command)
                self.undo_history.clear()  # Limpiar historial de deshacer
                
                # Limitar tamaño del historial
                if len(self.history) > self.max_history:
                    self.history.pop(0)
                
                return True
            else:
                output_manager.error(f"❌ Comando falló: {command.get_description()}")
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error ejecutando comando: {str(e)}")
            return False
    
    def undo_last_command(self) -> bool:
        """
        Deshace el último comando.
        
        Returns:
            True si el deshacer fue exitoso
        """
        if not self.history:
            output_manager.warning("⚠️ No hay comandos para deshacer")
            return False
        
        try:
            last_command = self.history.pop()
            if last_command.undo():
                self.undo_history.append(last_command)
                output_manager.info(f"↩️ Comando deshecho: {last_command.get_description()}")
                return True
            else:
                # Restaurar comando si el deshacer falló
                self.history.append(last_command)
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error deshaciendo comando: {str(e)}")
            return False
    
    def redo_last_command(self) -> bool:
        """
        Rehace el último comando deshecho.
        
        Returns:
            True si el rehacer fue exitoso
        """
        if not self.undo_history:
            output_manager.warning("⚠️ No hay comandos para rehacer")
            return False
        
        try:
            last_undone = self.undo_history.pop()
            if last_undone.execute():
                self.history.append(last_undone)
                output_manager.info(f"↪️ Comando rehecho: {last_undone.get_description()}")
                return True
            else:
                # Restaurar comando si el rehacer falló
                self.undo_history.append(last_undone)
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error rehaciendo comando: {str(e)}")
            return False
    
    def get_history(self) -> List[Command]:
        """Retorna el historial de comandos."""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Limpia el historial de comandos."""
        self.history.clear()
        self.undo_history.clear()
        output_manager.info("🧹 Historial de comandos limpiado")
    
    def get_history_summary(self) -> Dict[str, Any]:
        """Retorna un resumen del historial."""
        return {
            'total_commands': len(self.history),
            'undo_available': len(self.undo_history),
            'last_command': self.history[-1].get_description() if self.history else None
        }


class MacroCommand(Command):
    """
    Comando macro que ejecuta múltiples comandos.
    """
    
    def __init__(self, commands: List[Command], description: str):
        """
        Inicializa el comando macro.
        
        Args:
            commands: Lista de comandos a ejecutar
            description: Descripción del macro
        """
        self.commands = commands
        self.description = description
        self.executed_commands = []
    
    def execute(self) -> bool:
        """Ejecuta todos los comandos del macro."""
        try:
            self.executed_commands.clear()
            
            for command in self.commands:
                if command.execute():
                    self.executed_commands.append(command)
                else:
                    # Si un comando falla, deshacer los ejecutados
                    self._undo_executed_commands()
                    return False
            
            output_manager.success(f"✅ Macro ejecutado: {self.description}")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error ejecutando macro: {str(e)}")
            self._undo_executed_commands()
            return False
    
    def undo(self) -> bool:
        """Deshace todos los comandos del macro en orden inverso."""
        try:
            for command in reversed(self.executed_commands):
                command.undo()
            
            output_manager.info(f"↩️ Macro deshecho: {self.description}")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error deshaciendo macro: {str(e)}")
            return False
    
    def _undo_executed_commands(self) -> None:
        """Deshace los comandos ejecutados en orden inverso."""
        for command in reversed(self.executed_commands):
            try:
                command.undo()
            except Exception as e:
                output_manager.error(f"❌ Error deshaciendo comando: {str(e)}")
    
    def get_description(self) -> str:
        """Retorna la descripción del macro."""
        return self.description
