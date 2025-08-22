"""
Procesador de archivos para encontrar y organizar archivos TIFF
"""

from pathlib import Path
from typing import List, Dict, Any
import os


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
        tiff_extensions = ['.tiff', '.tif', '.TIFF', '.TIF']
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
                formats = ['jpg_400', 'jpg_200', 'pdf_easyocr']
                for format_name in formats:
                    format_dir = self.output_dir / format_name
                    format_dir.mkdir(exist_ok=True)
            
            print(f"Estructura de salida creada en: {self.output_dir}")
            return True
            
        except Exception as e:
            print(f"Error creando estructura de salida: {str(e)}")
            return False
    
    def get_output_path(self, input_file: Path, format_name: str, create_subdirectories: bool = True) -> Path:
        """
        Genera la ruta de salida para un archivo convertido
        
        Args:
            input_file: Archivo de entrada
            format_name: Nombre del formato de salida
            create_subdirectories: Si usar subdirectorios por formato
            
        Returns:
            Ruta de salida para el archivo convertido
        """
        if create_subdirectories:
            # Usar subdirectorios por formato
            output_dir = self.output_dir / format_name
        else:
            # Usar directorio principal
            output_dir = self.output_dir
        
        # Mantener estructura de directorios relativa si existe
        relative_path = input_file.relative_to(self.input_dir)
        if relative_path.parent != Path('.'):
            output_dir = output_dir / relative_path.parent
        
        # Crear directorio si no existe
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo con información específica del formato
        stem = input_file.stem
        
        if format_name == 'jpg_400':
            extension = '.jpg'
            filename = f"{stem}_400dpi{extension}"
        elif format_name == 'jpg_200':
            extension = '.jpg'
            filename = f"{stem}_200dpi{extension}"
        elif format_name == 'pdf_easyocr':
            extension = '.pdf'
            filename = f"{stem}_EasyOCR{extension}"
        else:
            extension = f".{format_name}"
            filename = f"{stem}{extension}"
        
        return output_dir / filename
    
    def validate_output_path(self, output_path: Path, overwrite: bool = False) -> bool:
        """
        Valida si se puede escribir en la ruta de salida
        
        Args:
            output_path: Ruta de salida a validar
            overwrite: Si permitir sobrescribir archivos existentes
            
        Returns:
            True si la ruta es válida para escritura
        """
        # Verificar si el archivo ya existe
        if output_path.exists() and not overwrite:
            print(f"Archivo ya existe (omitir): {output_path.name}")
            return False
        
        # Verificar permisos de escritura en el directorio padre
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Crear archivo temporal para probar permisos
            test_file = output_path.parent / f".test_{output_path.name}"
            test_file.touch()
            test_file.unlink()
            return True
        except Exception as e:
            print(f"Error validando ruta de salida {output_path}: {str(e)}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna un resumen del procesamiento de archivos"""
        total_files = len(self.tiff_files)
        total_size_mb = sum(self.get_file_info(f)['size_mb'] for f in self.tiff_files)
        
        return {
            'input_directory': str(self.input_dir),
            'output_directory': str(self.output_dir),
            'total_tiff_files': total_files,
            'total_size_mb': round(total_size_mb, 2),
            'files': self.get_all_files_info()
        }
