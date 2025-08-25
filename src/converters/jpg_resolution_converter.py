"""
Conversor de TIFF a JPG con resolución configurable
"""

import traceback
from pathlib import Path
from typing import Dict, Any

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
        self.quality = config.get("quality", 95)
        self.optimize = config.get("optimize", True)
        self.progressive = config.get("progressive", False)
        self.dpi = config.get("dpi", 300)

    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Convierte un archivo TIFF a JPG con la resolución especificada

        Args:
            input_path: Ruta del archivo TIFF de entrada
            output_path: Ruta del archivo JPG de salida

        Returns:
            True si la conversión fue exitosa
        """
        try:
            # Validar entrada
            if not self.validate_input(input_path):
                print(f"Error: Archivo de entrada inválido: {input_path}")
                return False

            # Crear directorio de salida
            if not self.create_output_directory(output_path):
                print(
                    f"Error: No se pudo crear el directorio de salida: {output_path.parent}"
                )
                return False

            # Abrir imagen TIFF
            with Image.open(input_path) as img:
                # Convertir a RGB si es necesario
                if img.mode not in ["RGB", "L"]:
                    img = img.convert("RGB")

                # Calcular nueva resolución basada en DPI
                original_dpi = img.info.get("dpi", (72, 72))[0]
                if original_dpi > 0:
                    scale_factor = self.dpi / original_dpi
                    # Limitar el factor de escala para evitar MemoryError
                    scale_factor = min(scale_factor, 2.0)
                    new_width = int(img.width * scale_factor)
                    new_height = int(img.height * scale_factor)

                    # Limitar dimensiones máximas
                    max_dimension = 8000
                    if new_width > max_dimension or new_height > max_dimension:
                        scale_factor = min(
                            max_dimension / img.width, max_dimension / img.height
                        )
                        new_width = int(img.width * scale_factor)
                        new_height = int(img.height * scale_factor)

                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Guardar como JPG
                img.save(
                    output_path,
                    "JPEG",
                    quality=self.quality,
                    optimize=self.optimize,
                    progressive=self.progressive,
                    dpi=(self.dpi, self.dpi),
                )

            print(f"✅ Convertido: {input_path.name} -> {output_path.name}")
            return True

        except Exception as e:
            print(f"❌ Error convirtiendo {input_path.name}: {str(e)}")
            traceback.print_exc()
            return False

    def get_file_extension(self) -> str:
        """Retorna la extensión del archivo JPG"""
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
        format_subdir = output_dir / f"jpg_{self.dpi}"
        format_subdir.mkdir(exist_ok=True)

        stem = input_path.stem
        extension = self.get_file_extension()
        filename = f"{stem}_{self.dpi}dpi{extension}"
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
