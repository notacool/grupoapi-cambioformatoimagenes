"""
Clase base para postconversores
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class BasePostConverter(ABC):
    """Clase base abstracta para todos los postconversores"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el postconversor base

        Args:
            config: Configuración del postconversor
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def process(self, conversion_result: Dict[str, Any], output_dir: Path) -> bool:
        """
        Procesa el resultado de la conversión

        Args:
            conversion_result: Resultado de la conversión principal
            output_dir: Directorio de salida

        Returns:
            True si el procesamiento fue exitoso
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Retorna el nombre del postconversor

        Returns:
            Nombre del postconversor
        """
        pass

    def _validate_config(self) -> None:
        """Valida la configuración del postconversor"""
        if not isinstance(self.config, dict):
            raise ValueError("La configuración debe ser un diccionario")

    def is_enabled(self) -> bool:
        """
        Verifica si el postconversor está habilitado

        Returns:
            True si está habilitado
        """
        return self.config.get("enabled", True)
