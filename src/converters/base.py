"""
Clase base para todos los conversores de archivos TIFF
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any


class BaseConverter(ABC):
    """Clase base abstracta para todos los conversores"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el conversor base

        Args:
            config: Configuración del conversor
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Convierte un archivo de entrada a un formato específico

        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida

        Returns:
            True si la conversión fue exitosa
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Retorna la extensión de archivo para este formato

        Returns:
            Extensión del archivo (ej: '.jpg', '.pdf')
        """
        pass

    def _validate_config(self) -> None:
        """Valida la configuración del conversor"""
        if not isinstance(self.config, dict):
            raise ValueError("La configuración debe ser un diccionario")

    def validate_input(self, input_path: Path) -> bool:
        """
        Valida si el archivo de entrada es válido

        Args:
            input_path: Ruta del archivo de entrada

        Returns:
            True si el archivo es válido
        """
        try:
            if not input_path.exists():
                print(f"Error: El archivo de entrada no existe: {input_path}")
                return False

            if not input_path.is_file():
                print(f"Error: La ruta de entrada no es un archivo: {input_path}")
                return False

            # Verificar extensión TIFF
            if input_path.suffix.lower() not in [".tiff", ".tif"]:
                print(f"Error: El archivo no es TIFF: {input_path}")
                return False

            return True

        except Exception as e:
            print(f"Error validando archivo de entrada: {str(e)}")
            return False

    def create_output_directory(self, output_path: Path) -> bool:
        """
        Crea el directorio de salida si no existe

        Args:
            output_path: Ruta del archivo de salida

        Returns:
            True si se creó correctamente
        """
        try:
            output_dir = output_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)
            return True

        except Exception as e:
            print(f"Error creando directorio de salida: {str(e)}")
            return False

    def get_output_filename(self, input_path: Path, output_dir: Path) -> Path:
        """
        Genera el nombre del archivo de salida

        Args:
            input_path: Archivo de entrada
            output_dir: Directorio de salida

        Returns:
            Ruta completa del archivo de salida
        """
        stem = input_path.stem
        extension = self.get_file_extension()
        filename = f"{stem}{extension}"
        return output_dir / filename

    def get_converter_info(self) -> Dict[str, Any]:
        """
        Retorna información del conversor

        Returns:
            Diccionario con información del conversor
        """
        return {
            "class": self.__class__.__name__,
            "config": self.config,
            "extension": self.get_file_extension(),
        }
