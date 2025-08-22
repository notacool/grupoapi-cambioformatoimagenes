"""
Ejemplo: Cómo agregar un nuevo conversor al sistema

Este archivo muestra cómo crear un conversor personalizado para el formato BMP
"""

from pathlib import Path
from typing import Dict, Any
from PIL import Image
from src.converters.base import BaseConverter


class BMPConverter(BaseConverter):
    """Conversor de TIFF a BMP"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Configuración específica para BMP
        self.bit_depth = config.get('bit_depth', 24)
        self.rle_compression = config.get('rle_compression', False)
    
    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Convierte una imagen TIFF a BMP
        
        Args:
            input_path: Ruta del archivo TIFF de entrada
            output_path: Ruta del archivo BMP de salida
            
        Returns:
            True si la conversión fue exitosa, False en caso contrario
        """
        try:
            # Validar entrada
            if not self.validate_input(input_path):
                print(f"Error: Archivo de entrada inválido: {input_path}")
                return False
            
            # Crear directorio de salida
            if not self.create_output_directory(output_path):
                print(f"Error: No se pudo crear el directorio de salida: {output_path.parent}")
                return False
            
            # Abrir imagen TIFF
            with Image.open(input_path) as img:
                # Convertir a RGB si es necesario
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Guardar como BMP
                img.save(
                    output_path,
                    'BMP',
                    bits=self.bit_depth
                )
                
                print(f"Convertido: {input_path.name} -> {output_path.name}")
                return True
                
        except Exception as e:
            print(f"Error convirtiendo {input_path.name} a BMP: {str(e)}")
            return False
    
    def get_file_extension(self) -> str:
        """Retorna la extensión .bmp"""
        return '.bmp'


# Para usar este conversor, necesitas:

# 1. Agregar la configuración en config.yaml:
"""
formats:
  # ... otros formatos ...
  bmp:
    enabled: true
    bit_depth: 24
    rle_compression: false
"""

# 2. Modificar src/converters/__init__.py para incluir:
"""
from .bmp_converter import BMPConverter
__all__ = ['BaseConverter', 'JPGConverter', 'PDFConverter', 'BMPConverter']
"""

# 3. Modificar src/converter.py en _initialize_converters():
"""
# BMP Converter
if self.config_manager.is_format_enabled('bmp'):
    bmp_config = self.config_manager.get_format_config('bmp')
    converters['bmp'] = BMPConverter(bmp_config)
"""

# 4. Guardar el archivo como src/converters/bmp_converter.py

if __name__ == '__main__':
    print("Este es un ejemplo de cómo crear un nuevo conversor.")
    print("Para usarlo, sigue los pasos comentados en el código.")
