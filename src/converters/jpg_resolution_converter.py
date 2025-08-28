"""
Conversor de TIFF a JPG con resolución configurable
"""

from pathlib import Path
from typing import Any, Dict

from PIL import Image

from ..output_manager import output_manager
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
                output_manager.error(
                    f"Error: Archivo de entrada inválido: {input_path}"
                )
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

    def get_output_filename(self, input_path: Path, output_dir: Path) -> Path:
        """
        Genera el nombre del archivo de salida con subdirectorio específico

        Args:
            input_path: Archivo de entrada
            output_dir: Directorio base de salida

        Returns:
            Ruta completa del archivo de salida
        """
        # Crear subdirectorio específico para este formato
        if self.dpi == 400:
            format_subdir = output_dir / "JPGHIGH"
        elif self.dpi == 200:
            format_subdir = output_dir / "JPGLOW"
        else:
            format_subdir = output_dir / f"JPG{self.dpi}"

        format_subdir.mkdir(exist_ok=True)

        # Generar nombre de archivo
        filename = f"{input_path.stem}{self.get_file_extension()}"

        return format_subdir / filename

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
