"""
Clase base abstracta para todos los conversores de imagen
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from PIL import Image


class BaseConverter(ABC):
    """Clase base para todos los conversores de imagen"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el conversor con configuración
        
        Args:
            config: Diccionario con configuración específica del formato
        """
        self.config = config
        self.format_name = self.__class__.__name__.replace('Converter', '').lower()
    
    @abstractmethod
    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Convierte una imagen del formato de entrada al formato de salida
        
        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            
        Returns:
            True si la conversión fue exitosa, False en caso contrario
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Devuelve la extensión de archivo para el formato de salida
        
        Returns:
            Extensión del archivo (ej: '.jpg', '.pdf')
        """
        pass
    
    def validate_input(self, input_path: Path) -> bool:
        """
        Valida que el archivo de entrada sea válido
        
        Args:
            input_path: Ruta del archivo de entrada
            
        Returns:
            True si el archivo es válido, False en caso contrario
        """
        return input_path.exists() and input_path.is_file()
    
    def create_output_directory(self, output_path: Path) -> bool:
        """
        Crea el directorio de salida si no existe
        
        Args:
            output_path: Ruta del archivo de salida
            
        Returns:
            True si se creó o ya existe el directorio
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    def get_output_filename(self, input_path: Path, output_dir: Path) -> Path:
        """
        Genera el nombre del archivo de salida
        
        Args:
            input_path: Ruta del archivo de entrada
            output_dir: Directorio de salida
            
        Returns:
            Ruta completa del archivo de salida
        """
        stem = input_path.stem
        extension = self.get_file_extension()
        return output_dir / f"{stem}{extension}"
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__} ({self.format_name})"
