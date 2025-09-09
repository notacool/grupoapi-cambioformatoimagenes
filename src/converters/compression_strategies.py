"""
Strategy Pattern para Compresión de PDF
======================================

Este módulo implementa el patrón Strategy para diferentes
estrategias de compresión de PDF.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from ..output_manager import output_manager


class CompressionStrategy(ABC):
    """
    Interfaz abstracta para estrategias de compresión.
    """
    
    @abstractmethod
    def compress(self, input_path: Path, output_path: Path, config: Dict[str, Any]) -> bool:
        """
        Comprime un archivo PDF.
        
        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            config: Configuración de compresión
            
        Returns:
            True si la compresión fue exitosa
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Retorna el nombre de la estrategia.
        
        Returns:
            Nombre de la estrategia
        """
        pass


class GhostscriptCompressionStrategy(CompressionStrategy):
    """
    Estrategia de compresión usando Ghostscript.
    """
    
    def compress(self, input_path: Path, output_path: Path, config: Dict[str, Any]) -> bool:
        """Comprime usando Ghostscript."""
        try:
            import subprocess
            import shutil
            
            # Buscar Ghostscript
            gs_path = shutil.which("gs") or shutil.which("gswin64c") or shutil.which("gswin32c")
            if not gs_path:
                output_manager.warning("⚠️ Ghostscript no encontrado")
                return False
            
            # Configurar nivel de compresión
            compression_level = config.get('compression_level', 'ebook')
            target_dpi = config.get('target_dpi', 200)
            
            # Comando Ghostscript
            cmd = [
                gs_path,
                "-sDEVICE=pdfwrite",
                f"-dPDFSETTINGS=/{compression_level}",
                f"-dDownsampleColorImages=true",
                f"-dColorImageResolution={target_dpi}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={output_path}",
                str(input_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_path.exists():
                output_manager.success(f"✅ Compresión Ghostscript exitosa: {output_path.name}")
                return True
            else:
                output_manager.error(f"❌ Error en compresión Ghostscript: {result.stderr}")
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error en compresión Ghostscript: {str(e)}")
            return False
    
    def get_name(self) -> str:
        return "Ghostscript"


class PikepdfCompressionStrategy(CompressionStrategy):
    """
    Estrategia de compresión usando pikepdf.
    """
    
    def compress(self, input_path: Path, output_path: Path, config: Dict[str, Any]) -> bool:
        """Comprime usando pikepdf."""
        try:
            import pikepdf
            
            with pikepdf.open(input_path) as pdf:
                # Configurar opciones de compresión
                save_options = {
                    "object_stream_mode": pikepdf.ObjectStreamMode.generate,
                    "compress_streams": True,
                    "preserve_pdfa": False,
                    "deterministic_id": False
                }
                
                # Eliminar metadatos si está configurado
                if config.get('remove_metadata', True):
                    pdf.docinfo.clear()
                
                pdf.save(output_path, **save_options)
                
                if output_path.exists():
                    output_manager.success(f"✅ Compresión pikepdf exitosa: {output_path.name}")
                    return True
                else:
                    output_manager.error("❌ Error: archivo de salida no creado")
                    return False
                    
        except Exception as e:
            output_manager.error(f"❌ Error en compresión pikepdf: {str(e)}")
            return False
    
    def get_name(self) -> str:
        return "pikepdf"


class PypdfCompressionStrategy(CompressionStrategy):
    """
    Estrategia de compresión usando pypdf.
    """
    
    def compress(self, input_path: Path, output_path: Path, config: Dict[str, Any]) -> bool:
        """Comprime usando pypdf."""
        try:
            from pypdf import PdfReader, PdfWriter
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Copiar páginas
            for page in reader.pages:
                writer.add_page(page)
            
            # Eliminar metadatos si está configurado
            if config.get('remove_metadata', True):
                writer.add_metadata({})
            
            # Escribir archivo
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            if output_path.exists():
                output_manager.success(f"✅ Compresión pypdf exitosa: {output_path.name}")
                return True
            else:
                output_manager.error("❌ Error: archivo de salida no creado")
                return False
                
        except Exception as e:
            output_manager.error(f"❌ Error en compresión pypdf: {str(e)}")
            return False
    
    def get_name(self) -> str:
        return "pypdf"


class CompressionContext:
    """
    Contexto que utiliza diferentes estrategias de compresión.
    """
    
    def __init__(self, strategy: CompressionStrategy):
        """
        Inicializa el contexto con una estrategia.
        
        Args:
            strategy: Estrategia de compresión a utilizar
        """
        self._strategy = strategy
    
    def set_strategy(self, strategy: CompressionStrategy) -> None:
        """
        Cambia la estrategia de compresión.
        
        Args:
            strategy: Nueva estrategia de compresión
        """
        self._strategy = strategy
        output_manager.info(f"🔄 Estrategia de compresión cambiada a: {strategy.get_name()}")
    
    def compress(self, input_path: Path, output_path: Path, config: Dict[str, Any]) -> bool:
        """
        Ejecuta la compresión usando la estrategia actual.
        
        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            config: Configuración de compresión
            
        Returns:
            True si la compresión fue exitosa
        """
        return self._strategy.compress(input_path, output_path, config)
    
    def get_strategy_name(self) -> str:
        """
        Retorna el nombre de la estrategia actual.
        
        Returns:
            Nombre de la estrategia
        """
        return self._strategy.get_name()


class CompressionStrategyFactory:
    """
    Factory para crear estrategias de compresión.
    """
    
    _strategies = {
        'ghostscript': GhostscriptCompressionStrategy,
        'pikepdf': PikepdfCompressionStrategy,
        'pypdf': PypdfCompressionStrategy,
    }
    
    @classmethod
    def create_strategy(cls, strategy_name: str) -> Optional[CompressionStrategy]:
        """
        Crea una estrategia de compresión.
        
        Args:
            strategy_name: Nombre de la estrategia
            
        Returns:
            Instancia de la estrategia o None si no está disponible
        """
        if strategy_name not in cls._strategies:
            output_manager.warning(f"⚠️ Estrategia '{strategy_name}' no disponible")
            return None
        
        try:
            strategy_class = cls._strategies[strategy_name]
            strategy = strategy_class()
            output_manager.info(f"✅ Estrategia '{strategy_name}' creada")
            return strategy
        except Exception as e:
            output_manager.error(f"❌ Error creando estrategia '{strategy_name}': {str(e)}")
            return None
    
    @classmethod
    def get_available_strategies(cls) -> list[str]:
        """
        Retorna las estrategias disponibles.
        
        Returns:
            Lista de nombres de estrategias
        """
        return list(cls._strategies.keys())
