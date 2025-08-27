"""
Procesador de archivos para el conversor TIFF
"""

import os
from pathlib import Path
from typing import List

from .output_manager import output_manager


class FileProcessor:
    """Procesa archivos y directorios para el conversor TIFF"""

    def __init__(self, input_dir: str, output_dir: str):
        """
        Inicializa el procesador de archivos

        Args:
            input_dir: Directorio de entrada
            output_dir: Directorio de salida
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self._tiff_files = None  # Lazy loading

    def _get_tiff_files(self) -> List[Path]:
        """Obtiene la lista de archivos TIFF del directorio de entrada"""
        tiff_files = []
        if self.input_dir.exists() and self.input_dir.is_dir():
            for file_path in self.input_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in [
                    ".tif",
                    ".tiff",
                ]:
                    tiff_files.append(file_path)

        output_manager.info(
            f"Encontrados {len(tiff_files)} archivos TIFF en: {self.input_dir}"
        )
        return tiff_files

    def get_tiff_files(self) -> List[Path]:
        """Retorna la lista de archivos TIFF"""
        if self._tiff_files is None:
            self._tiff_files = self._get_tiff_files()
        return self._tiff_files

    def create_output_structure(self, create_subdirs: bool = True) -> bool:
        """
        Crea la estructura de directorios de salida

        Args:
            create_subdirs: Si crear subdirectorios por formato

        Returns:
            True si se creó correctamente
        """
        try:
            # Crear directorio principal de salida
            self.output_dir.mkdir(parents=True, exist_ok=True)

            if create_subdirs:
                # Crear subdirectorios para cada formato
                subdirs = ["jpg_400", "jpg_200", "pdf_easyocr", "met_metadata"]

                for subdir in subdirs:
                    subdir_path = self.output_dir / subdir
                    subdir_path.mkdir(exist_ok=True)

            output_manager.info(f"Estructura de salida creada en: {self.output_dir}")
            return True

        except Exception as e:
            output_manager.error(f"Error creando estructura de salida: {str(e)}")
            return False

    def get_output_path(
        self, input_file: Path, format_name: str, create_subdirs: bool = True
    ) -> Path:
        """
        Genera la ruta de salida para un archivo

        Args:
            input_file: Archivo de entrada
            format_name: Nombre del formato de salida
            create_subdirs: Si crear subdirectorios

        Returns:
            Ruta de salida generada
        """
        if create_subdirs:
            # Crear subdirectorio para el formato
            format_dir = self.output_dir / format_name
            format_dir.mkdir(exist_ok=True)

            # Generar nombre de archivo
            if format_name == "jpg_400":
                filename = f"{input_file.stem}_400dpi.jpg"
            elif format_name == "jpg_200":
                filename = f"{input_file.stem}_200dpi.jpg"
            elif format_name == "pdf_easyocr":
                filename = f"{input_file.stem}_EasyOCR.pdf"
            elif format_name == "met_metadata":
                filename = f"{input_file.stem}_MET.xml"
            else:
                filename = (
                    f"{input_file.stem}_{format_name}{self._get_extension(format_name)}"
                )

            return format_dir / filename

        # Sin subdirectorios
        return (
            self.output_dir
            / f"{input_file.stem}_{format_name}{self._get_extension(format_name)}"
        )

    def _get_extension(self, format_name: str) -> str:
        """Retorna la extensión para un formato"""
        extensions = {
            "jpg_400": ".jpg",
            "jpg_200": ".jpg",
            "pdf_easyocr": ".pdf",
            "met_metadata": ".xml",
        }
        return extensions.get(format_name, "")

    def validate_output_path(self, output_path: Path, overwrite: bool = False) -> bool:
        """
        Valida si se puede escribir en la ruta de salida

        Args:
            output_path: Ruta de salida a validar
            overwrite: Si sobrescribir archivos existentes

        Returns:
            True si se puede escribir
        """
        try:
            output_dir = output_path.parent

            # Verificar si el directorio existe
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)

            # Verificar si el archivo ya existe
            if output_path.exists():
                if overwrite:
                    output_manager.info(
                        f"Sobrescribiendo archivo existente: {output_path.name}"
                    )
                    return True

                output_manager.info(f"Archivo ya existe (omitir): {output_path.name}")
                return False

            # Verificar permisos de escritura
            if not os.access(output_dir, os.W_OK):
                output_manager.error(f"Sin permisos de escritura en: {output_dir}")
                return False

            return True

        except Exception as e:
            output_manager.error(f"Error validando ruta de salida: {str(e)}")
            return False

    def cleanup_empty_directories(self) -> None:
        """Limpia directorios vacíos en el directorio de salida"""
        try:
            for item in self.output_dir.iterdir():
                if item.is_dir():
                    # Verificar si el directorio está vacío
                    if not any(item.iterdir()):
                        try:
                            item.rmdir()
                            output_manager.info(f"Directorio vacío eliminado: {item}")
                        except OSError as e:
                            output_manager.warning(
                                f"No se pudo eliminar directorio: {item} - {str(e)}"
                            )
        except Exception as e:
            output_manager.error(f"Error limpiando directorios vacíos: {str(e)}")
