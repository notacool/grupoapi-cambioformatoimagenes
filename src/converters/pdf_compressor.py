"""
Compresor de PDF con múltiples opciones de compresión.

Este módulo proporciona funcionalidad para comprimir archivos PDF
usando diferentes estrategias y herramientas.
"""

import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from ..output_manager import output_manager


class PDFCompressor:
    """
    Compresor de PDF con múltiples opciones de compresión.
    
    Soporta compresión usando:
    - Ghostscript (recomendado)
    - pikepdf (alternativa)
    - pypdf (básico)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el compresor de PDF.

        Args:
            config: Configuración del compresor
        """
        self.enabled = config.get("enabled", True)
        self.compression_level = config.get("compression_level", "ebook")
        self.target_dpi = config.get("target_dpi", 200)
        self.image_quality = config.get("image_quality", 85)
        self.remove_metadata = config.get("remove_metadata", True)
        self.fallback_on_error = config.get("fallback_on_error", True)
        
        # Validar nivel de compresión
        valid_levels = ["screen", "ebook", "printer", "prepress"]
        if self.compression_level not in valid_levels:
            output_manager.warning(
                f"⚠️ Nivel de compresión '{self.compression_level}' no válido. "
                f"Usando 'ebook' por defecto."
            )
            self.compression_level = "ebook"
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Verificar disponibilidad de herramientas
        self._check_tools_availability()

    def _check_tools_availability(self) -> None:
        """Verifica qué herramientas de compresión están disponibles."""
        self.ghostscript_available = self._check_ghostscript()
        self.pikepdf_available = self._check_pikepdf()
        self.pypdf_available = self._check_pypdf()
        
        if not any([self.ghostscript_available, self.pikepdf_available, self.pypdf_available]):
            output_manager.warning(
                "⚠️ No se encontraron herramientas de compresión PDF. "
                "La compresión estará deshabilitada."
            )
            self.enabled = False

    def _check_ghostscript(self) -> bool:
        """Verifica si Ghostscript está disponible."""
        try:
            # Probar diferentes nombres de Ghostscript según el sistema
            gs_names = ["gswin64c", "gswin32c", "gs", "ghostscript"]
            
            for gs_name in gs_names:
                try:
                    result = subprocess.run(
                        [gs_name, "--version"], 
                        capture_output=True, 
                        text=True, 
                        timeout=5
                    )
                    if result.returncode == 0:
                        output_manager.info(f"✅ Ghostscript disponible: {gs_name}")
                        self.ghostscript_name = gs_name
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return False
        except Exception:
            return False

    def _check_pikepdf(self) -> bool:
        """Verifica si pikepdf está disponible."""
        try:
            import pikepdf
            output_manager.info("✅ pikepdf disponible")
            return True
        except ImportError:
            return False

    def _check_pypdf(self) -> bool:
        """Verifica si pypdf está disponible."""
        try:
            from pypdf import PdfReader, PdfWriter
            output_manager.info("✅ pypdf disponible")
            return True
        except ImportError:
            return False

    def compress(self, input_path: Path, output_path: Path) -> bool:
        """
        Comprime un archivo PDF.

        Args:
            input_path: Ruta del PDF de entrada
            output_path: Ruta del PDF comprimido de salida

        Returns:
            True si la compresión fue exitosa
        """
        if not self.enabled:
            output_manager.info("🔄 Compresión de PDF deshabilitada")
            return True

        if not input_path.exists():
            output_manager.error(f"❌ Archivo de entrada no existe: {input_path}")
            return False

        # Obtener tamaño original
        original_size = input_path.stat().st_size / (1024 * 1024)  # MB
        
        output_manager.info(
            f"🔄 Comprimiendo PDF: {input_path.name} "
            f"({original_size:.1f} MB) -> {self.compression_level}"
        )

        # Intentar compresión con diferentes métodos
        success = False
        
        # Método 1: Ghostscript (mejor calidad)
        if self.ghostscript_available:
            success = self._compress_with_ghostscript(input_path, output_path)
        
        # Método 2: pikepdf (alternativa)
        if not success and self.pikepdf_available:
            success = self._compress_with_pikepdf(input_path, output_path)
        
        # Método 3: pypdf (básico)
        if not success and self.pypdf_available:
            success = self._compress_with_pypdf(input_path, output_path)
        
        # Si todos fallaron y fallback está habilitado
        if not success and self.fallback_on_error:
            output_manager.warning(
                "⚠️ Compresión falló, copiando archivo original"
            )
            shutil.copy2(input_path, output_path)
            success = True
        
        if success:
            # Mostrar estadísticas de compresión
            if output_path.exists():
                compressed_size = output_path.stat().st_size / (1024 * 1024)  # MB
                compression_ratio = ((original_size - compressed_size) / original_size) * 100
                
                output_manager.success(
                    f"✅ PDF comprimido: {input_path.name} "
                    f"({original_size:.1f} MB -> {compressed_size:.1f} MB, "
                    f"reducción: {compression_ratio:.1f}%)"
                )
        
        return success

    def _compress_with_ghostscript(self, input_path: Path, output_path: Path) -> bool:
        """
        Comprime PDF usando Ghostscript.

        Args:
            input_path: Ruta del PDF de entrada
            output_path: Ruta del PDF comprimido de salida

        Returns:
            True si la compresión fue exitosa
        """
        try:
            cmd = [
                self.ghostscript_name,
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS=/{self.compression_level}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                "-dAutoRotatePages=/None",
                "-dColorImageDownsampleType=/Bicubic",
                "-dColorImageResolution={}".format(self.target_dpi),
                "-dGrayImageDownsampleType=/Bicubic",
                "-dGrayImageResolution={}".format(self.target_dpi),
                "-dMonoImageDownsampleType=/Bicubic",
                "-dMonoImageResolution={}".format(self.target_dpi),
                "-dColorImageFilter=/DCTEncode",
                "-dGrayImageFilter=/DCTEncode",
                "-dMonoImageFilter=/CCITTFaxEncode",
                "-dJPEGQuality={}".format(self.image_quality),
                f"-sOutputFile={output_path}",
                str(input_path)
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            if result.returncode == 0 and output_path.exists():
                return True
            else:
                output_manager.warning(
                    f"⚠️ Ghostscript falló: {result.stderr}"
                )
                return False
                
        except subprocess.TimeoutExpired:
            output_manager.warning("⚠️ Ghostscript excedió el tiempo límite")
            return False
        except Exception as e:
            output_manager.warning(f"⚠️ Error con Ghostscript: {str(e)}")
            return False

    def _compress_with_pikepdf(self, input_path: Path, output_path: Path) -> bool:
        """
        Comprime PDF usando pikepdf.

        Args:
            input_path: Ruta del PDF de entrada
            output_path: Ruta del PDF comprimido de salida

        Returns:
            True si la compresión fue exitosa
        """
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
                
                # Si se quiere eliminar metadatos
                if self.remove_metadata:
                    pdf.docinfo.clear()
                
                pdf.save(output_path, **save_options)
                return True
                
        except Exception as e:
            output_manager.warning(f"⚠️ Error con pikepdf: {str(e)}")
            return False

    def _compress_with_pypdf(self, input_path: Path, output_path: Path) -> bool:
        """
        Compresión básica usando pypdf.

        Args:
            input_path: Ruta del PDF de entrada
            output_path: Ruta del PDF comprimido de salida

        Returns:
            True si la compresión fue exitosa
        """
        try:
            from pypdf import PdfReader, PdfWriter
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Copiar páginas
            for page in reader.pages:
                writer.add_page(page)
            
            # Configurar opciones básicas
            writer.add_metadata({})  # Metadatos mínimos
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            output_manager.warning(f"⚠️ Error con pypdf: {str(e)}")
            return False

    def get_compression_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre las herramientas de compresión disponibles.

        Returns:
            Diccionario con información de herramientas disponibles
        """
        return {
            "enabled": self.enabled,
            "compression_level": self.compression_level,
            "target_dpi": self.target_dpi,
            "image_quality": self.image_quality,
            "remove_metadata": self.remove_metadata,
            "tools_available": {
                "ghostscript": self.ghostscript_available,
                "pikepdf": self.pikepdf_available,
                "pypdf": self.pypdf_available
            }
        }
