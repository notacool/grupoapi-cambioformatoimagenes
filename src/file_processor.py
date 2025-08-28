"""
Procesador de archivos para el conversor TIFF
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

from .output_manager import output_manager


class FileProcessor:
    """Procesa archivos y directorios para el conversor TIFF"""

    def __init__(self, input_dir: str, output_dir: str):
        """
        Inicializa el procesador de archivos

        Args:
            input_dir: Directorio de entrada raíz
            output_dir: Directorio de salida raíz
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self._tiff_folders = None  # Lazy loading
        self._conversion_results = {}  # Resultados por subcarpeta

    def find_tiff_folders(self) -> Dict[str, Path]:
        """
        Busca recursivamente carpetas TIFF en el directorio de entrada

        Returns:
            Diccionario con {nombre_subcarpeta: ruta_carpeta_tiff}
        """
        tiff_folders = {}

        if not self.input_dir.exists() or not self.input_dir.is_dir():
            return tiff_folders

        # Buscar recursivamente en todas las subcarpetas
        for item in self.input_dir.rglob("*"):
            if item.is_dir() and item.name.upper() == "TIFF":
                # Obtener el nombre de la subcarpeta padre
                subfolder_name = item.parent.name
                tiff_folders[subfolder_name] = item
                output_manager.info(
                    f"📁 Carpeta TIFF encontrada en: {subfolder_name}/TIFF/"
                )

        return tiff_folders

    def get_tiff_folders(self) -> Dict[str, Path]:
        """Retorna las carpetas TIFF encontradas (lazy loading)"""
        if self._tiff_folders is None:
            self._tiff_folders = self.find_tiff_folders()
        return self._tiff_folders

    def get_tiff_files_from_folder(self, tiff_folder: Path) -> List[Path]:
        """
        Obtiene la lista de archivos TIFF de una carpeta específica

        Args:
            tiff_folder: Ruta a la carpeta TIFF

        Returns:
            Lista de archivos TIFF encontrados
        """
        tiff_files = []
        if tiff_folder.exists() and tiff_folder.is_dir():
            for file_path in tiff_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in [
                    ".tif",
                    ".tiff",
                ]:
                    tiff_files.append(file_path)

        return tiff_files

    def create_output_structure_for_subfolder(
        self, subfolder_name: str, enabled_formats: List[str]
    ) -> bool:
        """
        Crea la estructura de directorios de salida para una subcarpeta específica

        Args:
            subfolder_name: Nombre de la subcarpeta
            enabled_formats: Lista de formatos habilitados

        Returns:
            True si se creó correctamente
        """
        try:
            # Crear directorio de la subcarpeta en la salida
            subfolder_output_dir = self.output_dir / subfolder_name
            subfolder_output_dir.mkdir(parents=True, exist_ok=True)

            # Crear subdirectorios solo para los formatos habilitados
            for format_name in enabled_formats:
                format_dir = subfolder_output_dir / format_name
                format_dir.mkdir(exist_ok=True)

            output_manager.info(
                f"📂 Estructura creada para {subfolder_name}: {', '.join(enabled_formats)}"
            )
            return True

        except Exception as e:
            output_manager.error(
                f"❌ Error creando estructura para {subfolder_name}: {str(e)}"
            )
            return False

    def get_output_path_for_subfolder(
        self, input_file: Path, format_name: str, subfolder_name: str
    ) -> Path:
        """
        Genera la ruta de salida para un archivo en una subcarpeta específica

        Args:
            input_file: Archivo de entrada
            format_name: Nombre del formato de salida
            subfolder_name: Nombre de la subcarpeta

        Returns:
            Ruta de salida generada
        """
        # Crear estructura: output_dir/subfolder_name/format_name/
        format_dir = self.output_dir / subfolder_name / format_name
        format_dir.mkdir(parents=True, exist_ok=True)

        # Mantener nombre original del archivo
        stem = input_file.stem
        extension = self._get_extension_for_format(format_name)
        filename = f"{stem}{extension}"

        return format_dir / filename

    def _get_extension_for_format(self, format_name: str) -> str:
        """Retorna la extensión para un formato específico"""
        extensions = {
            "JPGHIGH": ".jpg",
            "JPGLOW": ".jpg",
            "PDF": ".pdf",
            "METS": ".xml",
        }
        return extensions.get(format_name, ".unknown")

    def validate_output_path(self, output_path: Path, overwrite: bool = False) -> bool:
        """
        Valida si se puede escribir en la ruta de salida

        Args:
            output_path: Ruta de salida a validar
            overwrite: Si sobrescribir archivos existentes

        Returns:
            True si la ruta es válida
        """
        try:
            # Crear directorio padre si no existe
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Verificar si el archivo existe y si se puede sobrescribir
            if output_path.exists() and not overwrite:
                output_manager.warning(
                    f"⚠️  Archivo existente (no sobrescrito): {output_path.name}"
                )
                return False

            return True

        except Exception as e:
            output_manager.error(f"❌ Error validando ruta de salida: {str(e)}")
            return False

    def add_conversion_result(self, subfolder_name: str, file_info: Dict) -> None:
        """
        Agrega un resultado de conversión para una subcarpeta

        Args:
            subfolder_name: Nombre de la subcarpeta
            file_info: Información del archivo convertido
        """
        if subfolder_name not in self._conversion_results:
            self._conversion_results[subfolder_name] = []

        self._conversion_results[subfolder_name].append(file_info)

    def get_conversion_results(self) -> Dict[str, List[Dict]]:
        """Retorna todos los resultados de conversión organizados por subcarpeta"""
        return self._conversion_results

    def get_summary_by_subfolder(self) -> Dict[str, Dict]:
        """
        Genera un resumen de conversiones por subcarpeta

        Returns:
            Diccionario con resumen por subcarpeta
        """
        summary = {}

        for subfolder_name, results in self._conversion_results.items():
            total_files = len(results)
            successful = len([r for r in results if r.get("success", False)])
            failed = total_files - successful

            summary[subfolder_name] = {
                "total_files": total_files,
                "successful": successful,
                "failed": failed,
                "formats_processed": list(set(r.get("format") for r in results)),
            }

        return summary
