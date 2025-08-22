"""
Conversor de imágenes TIFF a formato JPG con resolución configurable
"""

from pathlib import Path
from typing import Dict, Any
from PIL import Image
from .base import BaseConverter


class JPGResolutionConverter(BaseConverter):
    """Conversor de TIFF a JPG con resolución configurable"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Valores por defecto para JPG
        self.quality = config.get('quality', -1)
        self.optimize = config.get('optimize', True)
        self.progressive = config.get('progressive', False)
        self.dpi = config.get('dpi', 300)
        
        # En caso de que no este configurada la quality, se ajusta a la resolución
        if self.quality == -1:
            if self.dpi >= 400:
                self.quality = 95  # Alta calidad para 400 DPI
            elif self.dpi >= 200:
                self.quality = 90  # Calidad media para 200 DPI
        else:
            self.quality = 95
    
    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Convierte una imagen TIFF a JPG con resolución específica
        
        Args:
            input_path: Ruta del archivo TIFF de entrada
            output_path: Ruta del archivo JPG de salida
            
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
                # Obtener información de la imagen original
                original_dpi = img.info.get('dpi', (300, 300))[0]
                
                # Calcular factor de escala para la resolución deseada
                scale_factor = self.dpi / original_dpi
                
                # Limitar el factor de escala para evitar problemas de memoria
                max_scale = 2.0  # Máximo 2x el tamaño original
                if scale_factor > max_scale:
                    print(f"⚠️  Factor de escala {scale_factor:.2f} muy alto, limitando a {max_scale}")
                    scale_factor = max_scale
                
                new_size = tuple(int(dim * scale_factor) for dim in img.size)
                
                # Verificar que el tamaño no sea excesivo
                max_dimension = 8000  # Máximo 8000 píxeles en cualquier dimensión
                if max(new_size) > max_dimension:
                    print(f"⚠️  Tamaño {new_size} muy grande, limitando dimensiones")
                    if new_size[0] > max_dimension:
                        new_size = (max_dimension, int(new_size[1] * max_dimension / new_size[0]))
                    if new_size[1] > max_dimension:
                        new_size = (int(new_size[0] * max_dimension / new_size[1]), max_dimension)
                
                # Redimensionar imagen si es necesario
                if scale_factor != 1.0:
                    print(f"Redimensionando de {img.size} a {new_size} (factor: {scale_factor:.2f})")
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Convertir a RGB si es necesario (JPG no soporta transparencia)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Crear fondo blanco para transparencias
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Guardar como JPG con la resolución especificada
                img.save(
                    output_path,
                    'JPEG',
                    quality=self.quality,
                    optimize=self.optimize,
                    progressive=self.progressive,
                    dpi=(self.dpi, self.dpi)
                )
                
                print(f"Convertido: {input_path.name} -> {output_path.name} ({self.dpi} DPI)")
                return True
                
        except Exception as e:
            print(f"Error convirtiendo {input_path.name} a JPG {self.dpi} DPI: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_file_extension(self) -> str:
        """Retorna la extensión .jpg"""
        return '.jpg'
    
    def get_output_filename(self, input_path: Path, output_dir: Path) -> Path:
        """
        Genera el nombre del archivo de salida con DPI
        
        Args:
            input_path: Archivo de entrada
            output_dir: Directorio de salida
            
        Returns:
            Ruta del archivo de salida
        """
        stem = input_path.stem
        extension = self.get_file_extension()
        
        # Crear subdirectorio específico para este formato
        format_dir = output_dir / f"jpg_{self.dpi}"
        format_dir.mkdir(parents=True, exist_ok=True)
        
        return format_dir / f"{stem}_{self.dpi}dpi{extension}"
