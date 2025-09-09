"""
Builder Pattern para Configuración
=================================

Este módulo implementa el patrón Builder para crear
configuraciones complejas de manera fluida y validada.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from output_manager import output_manager


class ConfigBuilder:
    """
    Builder para crear configuraciones del sistema.
    
    Permite construir configuraciones complejas paso a paso
    con validación y valores por defecto.
    """
    
    def __init__(self):
        """Inicializa el builder con configuración vacía."""
        self.config = {
            'formats': {},
            'postconverters': {},
            'metadata': {},
            'system': {}
        }
        self._current_format = None
        self._current_postconverter = None
    
    def add_format(self, name: str) -> 'ConfigBuilder':
        """
        Agrega un formato a la configuración.
        
        Args:
            name: Nombre del formato
            
        Returns:
            Self para method chaining
        """
        self._current_format = name
        self.config['formats'][name] = {
            'enabled': True,
            'quality': 95,
            'optimize': True,
            'progressive': False
        }
        return self
    
    def set_format_enabled(self, enabled: bool) -> 'ConfigBuilder':
        """
        Establece si el formato está habilitado.
        
        Args:
            enabled: Si el formato está habilitado
            
        Returns:
            Self para method chaining
        """
        if self._current_format:
            self.config['formats'][self._current_format]['enabled'] = enabled
        return self
    
    def set_format_quality(self, quality: int) -> 'ConfigBuilder':
        """
        Establece la calidad del formato.
        
        Args:
            quality: Calidad (1-100)
            
        Returns:
            Self para method chaining
        """
        if self._current_format and 1 <= quality <= 100:
            self.config['formats'][self._current_format]['quality'] = quality
        return self
    
    def set_format_dpi(self, dpi: int) -> 'ConfigBuilder':
        """
        Establece la resolución DPI del formato.
        
        Args:
            dpi: Resolución en DPI
            
        Returns:
            Self para method chaining
        """
        if self._current_format and dpi > 0:
            self.config['formats'][self._current_format]['dpi'] = dpi
        return self
    
    def set_format_optimize(self, optimize: bool) -> 'ConfigBuilder':
        """
        Establece si optimizar el formato.
        
        Args:
            optimize: Si optimizar
            
        Returns:
            Self para method chaining
        """
        if self._current_format:
            self.config['formats'][self._current_format]['optimize'] = optimize
        return self
    
    def add_pdf_config(self, resolution: int = 300, page_size: str = "A4") -> 'ConfigBuilder':
        """
        Agrega configuración específica para PDF.
        
        Args:
            resolution: Resolución en DPI
            page_size: Tamaño de página
            
        Returns:
            Self para method chaining
        """
        if self._current_format:
            self.config['formats'][self._current_format].update({
                'resolution': resolution,
                'page_size': page_size,
                'fit_to_page': True,
                'ocr_language': ["es", "en"],
                'ocr_confidence': 0.2,
                'create_searchable_pdf': True
            })
        return self
    
    def add_postconverter(self, name: str) -> 'ConfigBuilder':
        """
        Agrega un postconversor a la configuración.
        
        Args:
            name: Nombre del postconversor
            
        Returns:
            Self para method chaining
        """
        self._current_postconverter = name
        self.config['postconverters'][name] = {
            'enabled': True
        }
        return self
    
    def set_postconverter_enabled(self, enabled: bool) -> 'ConfigBuilder':
        """
        Establece si el postconversor está habilitado.
        
        Args:
            enabled: Si el postconversor está habilitado
            
        Returns:
            Self para method chaining
        """
        if self._current_postconverter:
            self.config['postconverters'][self._current_postconverter]['enabled'] = enabled
        return self
    
    def set_pdf_max_size(self, max_size_mb: int) -> 'ConfigBuilder':
        """
        Establece el tamaño máximo del PDF consolidado.
        
        Args:
            max_size_mb: Tamaño máximo en MB
            
        Returns:
            Self para method chaining
        """
        if self._current_postconverter == 'consolidated_pdf':
            self.config['postconverters']['consolidated_pdf']['max_size_mb'] = max_size_mb
        return self
    
    def add_compression_config(self, level: str = "ebook", target_dpi: int = 200) -> 'ConfigBuilder':
        """
        Agrega configuración de compresión.
        
        Args:
            level: Nivel de compresión
            target_dpi: DPI objetivo
            
        Returns:
            Self para method chaining
        """
        if self._current_postconverter:
            self.config['postconverters'][self._current_postconverter]['compression'] = {
                'enabled': True,
                'compression_level': level,
                'target_dpi': target_dpi,
                'image_quality': 85,
                'remove_metadata': True
            }
        return self
    
    def add_metadata_config(self, organization: str = "Grupo API", creator: str = "Sistema Automatizado") -> 'ConfigBuilder':
        """
        Agrega configuración de metadatos.
        
        Args:
            organization: Nombre de la organización
            creator: Sistema creador
            
        Returns:
            Self para method chaining
        """
        self.config['metadata'] = {
            'organization': organization,
            'creator': creator,
            'generate_all_met': False
        }
        return self
    
    def add_system_config(self, max_workers: int = None, log_level: str = "INFO") -> 'ConfigBuilder':
        """
        Agrega configuración del sistema.
        
        Args:
            max_workers: Número máximo de workers
            log_level: Nivel de logging
            
        Returns:
            Self para method chaining
        """
        self.config['system'] = {
            'max_workers': max_workers,
            'log_level': log_level,
            'temp_dir': None
        }
        return self
    
    def validate(self) -> bool:
        """
        Valida la configuración construida.
        
        Returns:
            True si la configuración es válida
        """
        try:
            # Validar formatos
            for format_name, format_config in self.config['formats'].items():
                if not isinstance(format_config.get('enabled'), bool):
                    output_manager.error(f"❌ Formato '{format_name}': 'enabled' debe ser booleano")
                    return False
                
                quality = format_config.get('quality', 95)
                if not (1 <= quality <= 100):
                    output_manager.error(f"❌ Formato '{format_name}': 'quality' debe estar entre 1 y 100")
                    return False
            
            # Validar postconversores
            for postconverter_name, postconverter_config in self.config['postconverters'].items():
                if not isinstance(postconverter_config.get('enabled'), bool):
                    output_manager.error(f"❌ Postconversor '{postconverter_name}': 'enabled' debe ser booleano")
                    return False
            
            output_manager.success("✅ Configuración validada correctamente")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error validando configuración: {str(e)}")
            return False
    
    def build(self) -> Dict[str, Any]:
        """
        Construye y retorna la configuración final.
        
        Returns:
            Configuración construida
        """
        if self.validate():
            output_manager.success("✅ Configuración construida exitosamente")
            return self.config.copy()
        else:
            raise ValueError("Configuración inválida")
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Guarda la configuración en un archivo YAML.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            import yaml
            
            config = self.build()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            output_manager.success(f"✅ Configuración guardada en: {file_path}")
            return True
            
        except Exception as e:
            output_manager.error(f"❌ Error guardando configuración: {str(e)}")
            return False


class ProductionConfigBuilder(ConfigBuilder):
    """
    Builder especializado para configuraciones de producción.
    """
    
    def build_production_config(self) -> Dict[str, Any]:
        """
        Construye una configuración optimizada para producción.
        
        Returns:
            Configuración de producción
        """
        return (self
                .add_format("JPGHIGH")
                .set_format_quality(95)
                .set_format_dpi(400)
                .set_format_optimize(True)
                
                .add_format("JPGLOW")
                .set_format_quality(90)
                .set_format_dpi(200)
                .set_format_optimize(True)
                
                .add_format("PDF")
                .add_pdf_config(resolution=300, page_size="A4")
                
                .add_postconverter("consolidated_pdf")
                .set_pdf_max_size(5000)  # 5GB
                .add_compression_config(level="ebook", target_dpi=200)
                
                .add_postconverter("met_format")
                .set_postconverter_enabled(True)
                
                .add_metadata_config("Grupo API", "Sistema Automatizado")
                .add_system_config(max_workers=4, log_level="INFO")
                .build())


class DevelopmentConfigBuilder(ConfigBuilder):
    """
    Builder especializado para configuraciones de desarrollo.
    """
    
    def build_development_config(self) -> Dict[str, Any]:
        """
        Construye una configuración optimizada para desarrollo.
        
        Returns:
            Configuración de desarrollo
        """
        return (self
                .add_format("JPGHIGH")
                .set_format_quality(85)
                .set_format_dpi(300)
                .set_format_optimize(False)
                
                .add_format("PDF")
                .add_pdf_config(resolution=200, page_size="A4")
                
                .add_postconverter("consolidated_pdf")
                .set_pdf_max_size(100)  # 100MB para desarrollo
                .add_compression_config(level="screen", target_dpi=150)
                
                .add_metadata_config("Desarrollo", "Sistema de Pruebas")
                .add_system_config(max_workers=2, log_level="DEBUG")
                .build())
