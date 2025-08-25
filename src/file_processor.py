"""
Procesador de archivos para encontrar y organizar archivos TIFF
"""

from pathlib import Path
from typing import List, Dict, Any


class FileProcessor:
    """Procesador de archivos TIFF"""

    def __init__(self, input_dir: str, output_dir: str):
        """
        Inicializa el procesador de archivos

        Args:
            input_dir: Directorio de entrada con archivos TIFF
            output_dir: Directorio de salida para las conversiones
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.tiff_files = []
        self._scan_tiff_files()

    def _scan_tiff_files(self) -> None:
        """Escanea el directorio de entrada en busca de archivos TIFF"""
        if not self.input_dir.exists():
            raise ValueError(f"El directorio de entrada no existe: {self.input_dir}")

        if not self.input_dir.is_dir():
            raise ValueError(f"La ruta de entrada no es un directorio: {self.input_dir}")

        # Buscar archivos TIFF (case-insensitive)
        self.tiff_files = []

        for file_path in self.input_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.tiff', '.tif']:
                self.tiff_files.append(file_path)

        print(f"Encontrados {len(self.tiff_files)} archivos TIFF en: {self.input_dir}")

    def get_tiff_files(self) -> List[Path]:
        """Retorna la lista de archivos TIFF encontrados"""
        return self.tiff_files.copy()

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Obtiene información detallada de un archivo TIFF

        Args:
            file_path: Ruta del archivo

        Returns:
            Diccionario con información del archivo
        """
        try:
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': stat.st_mtime,
                'relative_path': file_path.relative_to(self.input_dir),
                'absolute_path': str(file_path)
            }
        except Exception as e:
            return {
                'name': file_path.name,
                'error': str(e),
                'relative_path': file_path.relative_to(self.input_dir),
                'absolute_path': str(file_path)
            }

    def get_all_files_info(self) -> List[Dict[str, Any]]:
        """Retorna información de todos los archivos TIFF"""
        return [self.get_file_info(file_path) for file_path in self.tiff_files]

    def create_output_structure(self, create_subdirectories: bool = True) -> bool:
        """
        Crea la estructura de directorios de salida

        Args:
            create_subdirectories: Si crear subdirectorios para cada formato

        Returns:
            True si se creó correctamente
        """
        try:
            # Crear directorio principal de salida
            self.output_dir.mkdir(parents=True, exist_ok=True)

            if create_subdirectories:
                # Crear subdirectorios para cada formato
                formats = ['jpg_400', 'jpg_200', 'pdf_easyocr', 'met_metadata']
                for format_name in formats:
                    format_dir = self.output_dir / format_name
                    format_dir.mkdir(exist_ok=True)

            print(f"Estructura de salida creada en: {self.output_dir}")
            return True

        except Exception as e:
            print(f"Error creando estructura de salida: {str(e)}")
            return False

    def get_output_path(self, input_file: Path, format_name: str,
                       create_subdirectories: bool = True) -> Path:
        """
        Genera la ruta de salida para un archivo convertido

        Args:
            input_file: Archivo de entrada
            format_name: Nombre del formato de salida
            create_subdirectories: Si usar subdirectorios

        Returns:
            Ruta de salida generada
        """
        if create_subdirectories:
            # Crear subdirectorio para el formato
            format_dir = self.output_dir / format_name
            format_dir.mkdir(exist_ok=True)
            output_dir = format_dir
        else:
            output_dir = self.output_dir

        # Generar nombre de archivo de salida
        stem = input_file.stem
        extension = self._get_format_extension(format_name)
        output_filename = f"{stem}_{format_name}{extension}"

        return output_dir / output_filename

    def _get_format_extension(self, format_name: str) -> str:
        """Obtiene la extensión de archivo para un formato específico"""
        extensions = {
            'jpg_400': '.jpg',
            'jpg_200': '.jpg',
            'pdf_easyocr': '.pdf',
            'met_metadata': '.xml'
        }
        return extensions.get(format_name, '.unknown')

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
            # Verificar si el archivo ya existe
            if output_path.exists():
                if not overwrite:
                    print(f"Archivo ya existe (omitir): {output_path.name}")
                    return False
                print(f"Sobrescribiendo archivo existente: {output_path.name}")

            # Verificar si se puede escribir en el directorio
            output_dir = output_path.parent
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)

            # Verificar permisos de escritura
            try:
                # Crear archivo temporal para probar permisos
                test_file = output_dir / ".test_write_permissions"
                test_file.touch()
                test_file.unlink()
            except Exception:
                print(f"Sin permisos de escritura en: {output_dir}")
                return False

            return True

        except Exception as e:
            print(f"Error validando ruta de salida: {str(e)}")
            return False

    def get_directory_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del directorio de entrada

        Returns:
            Diccionario con estadísticas
        """
        try:
            total_files = len(self.tiff_files)
            total_size = sum(file_path.stat().st_size for file_path in self.tiff_files)
            total_size_mb = round(total_size / (1024 * 1024), 2)

            # Agrupar por extensión
            extensions = {}
            for file_path in self.tiff_files:
                ext = file_path.suffix.lower()
                if ext not in extensions:
                    extensions[ext] = []
                extensions[ext].append(file_path)

            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': total_size_mb,
                'extensions': {ext: len(files) for ext, files in extensions.items()},
                'input_directory': str(self.input_dir),
                'output_directory': str(self.output_dir)
            }

        except Exception as e:
            return {
                'error': str(e),
                'input_directory': str(self.input_dir),
                'output_directory': str(self.output_dir)
            }

    def cleanup_empty_directories(self) -> bool:
        """
        Elimina directorios vacíos en la salida

        Returns:
            True si se limpió correctamente
        """
        try:
            if not self.output_dir.exists():
                return True

            # Buscar directorios vacíos recursivamente
            for dir_path in sorted(self.output_dir.rglob('*'), reverse=True):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    try:
                        dir_path.rmdir()
                        print(f"Directorio vacío eliminado: {dir_path}")
                    except Exception as e:
                        print(f"No se pudo eliminar directorio: {dir_path} - {str(e)}")

            return True

        except Exception as e:
            print(f"Error limpiando directorios vacíos: {str(e)}")
            return False
