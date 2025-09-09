"""
Factory Pattern para Conversores
===============================

Este módulo implementa el patrón Factory Method para crear conversores
de manera dinámica y extensible.
"""

from typing import Dict, Any, Type, Optional
from .base import BaseConverter
from .jpg_resolution_converter import JPGResolutionConverter
from .pdf_easyocr_converter import PDFEasyOCRConverter
from .met_metadata_converter import METMetadataConverter
from ..output_manager import output_manager


class ConverterFactory:
    """
    Factory para crear conversores de manera dinámica.
    
    Permite registrar nuevos conversores y crearlos basándose en
    la configuración sin modificar el código principal.
    """
    
    # Registro de conversores disponibles
    _converters: Dict[str, Type[BaseConverter]] = {
        'JPGHIGH': JPGResolutionConverter,
        'JPGLOW': JPGResolutionConverter,
        'PDF': PDFEasyOCRConverter,
        'MET': METMetadataConverter,
    }
    
    @classmethod
    def register_converter(cls, name: str, converter_class: Type[BaseConverter]) -> None:
        """
        Registra un nuevo conversor en el factory.
        
        Args:
            name: Nombre del conversor
            converter_class: Clase del conversor
        """
        if not issubclass(converter_class, BaseConverter):
            raise ValueError(f"El conversor {name} debe heredar de BaseConverter")
        
        cls._converters[name] = converter_class
        output_manager.info(f"✅ Conversor '{name}' registrado en el factory")
    
    @classmethod
    def create_converter(cls, name: str, config: Dict[str, Any]) -> Optional[BaseConverter]:
        """
        Crea un conversor basándose en el nombre y configuración.
        
        Args:
            name: Nombre del conversor
            config: Configuración del conversor
            
        Returns:
            Instancia del conversor o None si no está disponible
        """
        if name not in cls._converters:
            output_manager.warning(f"⚠️ Conversor '{name}' no registrado en el factory")
            return None
        
        try:
            converter_class = cls._converters[name]
            converter = converter_class(config)
            output_manager.info(f"✅ Conversor '{name}' creado exitosamente")
            return converter
        except Exception as e:
            output_manager.error(f"❌ Error creando conversor '{name}': {str(e)}")
            return None
    
    @classmethod
    def get_available_converters(cls) -> list[str]:
        """
        Retorna la lista de conversores disponibles.
        
        Returns:
            Lista de nombres de conversores
        """
        return list(cls._converters.keys())
    
    @classmethod
    def create_converters_from_config(cls, config_manager) -> Dict[str, BaseConverter]:
        """
        Crea todos los conversores habilitados basándose en la configuración.
        
        Args:
            config_manager: Gestor de configuración
            
        Returns:
            Diccionario de conversores creados
        """
        converters = {}
        enabled_formats = config_manager.get_enabled_formats()
        
        for format_name in enabled_formats:
            format_config = config_manager.get_format_config(format_name)
            converter = cls.create_converter(format_name, format_config)
            
            if converter:
                converters[format_name] = converter
        
        output_manager.info(f"📋 Conversores creados: {list(converters.keys())}")
        return converters


class PostConverterFactory:
    """
    Factory para crear postconversores de manera dinámica.
    """
    
    # Registro de postconversores disponibles
    _postconverters: Dict[str, Type] = {}
    
    @classmethod
    def register_postconverter(cls, name: str, postconverter_class: Type) -> None:
        """
        Registra un nuevo postconversor en el factory.
        
        Args:
            name: Nombre del postconversor
            postconverter_class: Clase del postconversor
        """
        cls._postconverters[name] = postconverter_class
        output_manager.info(f"✅ Postconversor '{name}' registrado en el factory")
    
    @classmethod
    def create_postconverter(cls, name: str, config: Dict[str, Any]) -> Optional[Any]:
        """
        Crea un postconversor basándose en el nombre y configuración.
        
        Args:
            name: Nombre del postconversor
            config: Configuración del postconversor
            
        Returns:
            Instancia del postconversor o None si no está disponible
        """
        if name not in cls._postconverters:
            output_manager.warning(f"⚠️ Postconversor '{name}' no registrado en el factory")
            return None
        
        try:
            postconverter_class = cls._postconverters[name]
            postconverter = postconverter_class(config)
            output_manager.info(f"✅ Postconversor '{name}' creado exitosamente")
            return postconverter
        except Exception as e:
            output_manager.error(f"❌ Error creando postconversor '{name}': {str(e)}")
            return None
