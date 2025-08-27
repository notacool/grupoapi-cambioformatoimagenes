"""
Conversor de TIFF a JPG con resolución configurable
"""

import traceback
from pathlib import Path
from typing import Any, Dict

from PIL import Image

from .base import BaseConverter


class JPGResolutionConverter(BaseConverter):
    """Conversor de TIFF a JPG con resolución configurable"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el conversor JPG

        Args:
            config: Configuración del conversor
        """
        super().__init__(config)
        self.quality = config.get("quality", 90)
        self.optimize = config.get("optimize", True)
        self.progressive = config.get("progressive", False)
        self.dpi = config.get("dpi", 200)

    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Convierte un archivo TIFF a JPG

        Args:
            input_path: Ruta del archivo TIFF de entrada
            output_path: Ruta del archivo JPG de salida

        Returns:
            True si la conversión fue exitosa
        """
        try:
            # Validar entrada
            if not self.validate_input(input_path):
                output_manager.error(f"Error: Archivo de entrada inválido: {input_path}")
                return False

            # Crear directorio de salida
            if not self.create_output_directory(output_path):
                output_manager.error(
                    f"Error: No se pudo crear el directorio de salida: {output_path.parent}"
                )
                return False

            # Abrir imagen TIFF
            with Image.open(input_path) as img:
                # Convertir a RGB si es necesario
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                # Guardar como JPG
                img.save(
                    output_path,
                    "JPEG",
                    quality=self.quality,
                    optimize=self.optimize,
                    progressive=self.progressive,
                    dpi=(self.dpi, self.dpi),
                )

            return True

        except Exception as e:
            output_manager.error(f"❌ Error convirtiendo {input_path.name}: {str(e)}")
            return False

    def get_file_extension(self) -> str:
        """Retorna la extensión del archivo de salida"""
        return ".jpg"

    def get_output_filename(self, input_file: Path, output_dir: Path) -> Path:
        """
        Genera el nombre del archivo de salida

        Args:
            input_file: Archivo de entrada
            output_dir: Directorio de salida

        Returns:
            Ruta del archivo de salida
        """
        if self.dpi == 400:
            filename = f"{input_file.stem}_400dpi.jpg"
        elif self.dpi == 200:
            filename = f"{input_file.stem}_200dpi.jpg"
        else:
            filename = f"{input_file.stem}_{self.dpi}dpi.jpg"
        
        return output_dir / filename

    def get_converter_info(self) -> Dict[str, Any]:
        """
        Retorna información específica del conversor JPG

        Returns:
            Diccionario con información del conversor
        """
        base_info = super().get_converter_info()
        base_info.update(
            {
                "quality": self.quality,
                "optimize": self.optimize,
                "progressive": self.progressive,
                "dpi": self.dpi,
                "format": "JPEG",
            }
        )
        return base_info
