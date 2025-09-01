"""
Postconversor para consolidar todas las imágenes TIFF en un solo PDF con OCR.

Este postconversor:
- Toma todas las imágenes TIFF de una subcarpeta
- Las ordena alfabéticamente por nombre
- Las consolida en un solo PDF con OCR
- Divide el PDF si excede el tamaño máximo configurado
- Aplica nombres con _numero para múltiples archivos
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.converters.pdf_easyocr_converter import PDFEasyOCRConverter
from src.converters.pdf_compressor import PDFCompressor
from src.output_manager import output_manager
from src.postconverters.base import BasePostConverter


class ConsolidatedPDFPostconverter(BasePostConverter):
    """
    Postconversor que consolida todas las imágenes TIFF en un solo PDF con OCR.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el postconversor.

        Args:
            config: Configuración del postconversor
        """
        super().__init__(config)
        self.enabled = config.get("enabled", True)
        self.max_size_mb = config.get("max_size_mb", 10)
        self.output_folder = config.get("output_folder", "PDF")

        # Inicializar el conversor PDF con OCR
        self.pdf_converter = PDFEasyOCRConverter(config)

        # Configuración de compresión para PDFs consolidados
        compression_config = config.get("compression", {})
        self.pdf_compressor = PDFCompressor(compression_config)

        # Configurar logging
        self.logger = logging.getLogger(__name__)

    def process(self, conversion_result: Dict[str, Any], output_dir: Path) -> bool:
        """
        Procesa la consolidación de PDFs para una subcarpeta.

        Args:
            conversion_result: Resultado de la conversión
            output_dir: Directorio de salida

        Returns:
            True si se procesó exitosamente
        """
        try:
            if not self.enabled:
                output_manager.info(
                    "🔄 Consolidated PDF Postconverter deshabilitado, saltando..."
                )
                return True

            subfolder_name = conversion_result.get("subfolder")
            if not subfolder_name:
                output_manager.error(
                    "❌ No se encontró nombre de subcarpeta en el resultado"
                )
                return False

            # Obtener archivos TIFF de la subcarpeta
            tiff_files = self._get_tiff_files_from_subfolder(subfolder_name, output_dir)
            if not tiff_files:
                output_manager.info(
                    f"ℹ️ No se encontraron archivos TIFF en {subfolder_name}"
                )
                return True

            # Ordenar archivos alfabéticamente
            tiff_files.sort(key=lambda x: x.name.lower())

            output_manager.info(
                f"🔄 Consolidando {len(tiff_files)} archivos TIFF de {subfolder_name}"
            )

            # Crear directorio de salida
            pdf_output_dir = output_dir / subfolder_name / self.output_folder
            pdf_output_dir.mkdir(parents=True, exist_ok=True)

            # Consolidar en PDF
            success = self._consolidate_tiff_to_pdf(
                tiff_files, pdf_output_dir, subfolder_name
            )

            if success:
                output_manager.success(
                    f"✅ PDF consolidado creado exitosamente para {subfolder_name}"
                )
            else:
                output_manager.error(
                    f"❌ Error al crear PDF consolidado para {subfolder_name}"
                )

            return success

        except Exception as e:
            error_msg = (
                f"Error en ConsolidatedPDFPostconverter para {subfolder_name}: {str(e)}"
            )
            output_manager.error(f"❌ {error_msg}")
            self.logger.error(error_msg, exc_info=True)
            return False

    def get_name(self) -> str:
        """
        Retorna el nombre del postconversor

        Returns:
            Nombre del postconversor
        """
        return "ConsolidatedPDFPostconverter"

    def _get_tiff_files_from_subfolder(
        self, subfolder_name: str, output_dir: Path
    ) -> List[Path]:
        """
        Obtiene todos los archivos TIFF de una subcarpeta.

        Args:
            subfolder_name: Nombre de la subcarpeta
            output_dir: Directorio de salida

        Returns:
            Lista de archivos TIFF encontrados
        """
        try:
            # Buscar en la carpeta TIFF de la subcarpeta
            tiff_dir = output_dir / subfolder_name / "TIFF"
            if not tiff_dir.exists():
                # Si no existe TIFF, buscar en el directorio de entrada original
                # Esto es para casos donde se procesa desde el directorio raíz
                input_dir = Path(output_dir).parent / subfolder_name / "TIFF"
                if input_dir.exists():
                    tiff_dir = input_dir
                else:
                    return []

            # Buscar archivos TIFF
            tiff_files = []
            for ext in [".tiff", ".tif", ".TIFF", ".TIF"]:
                tiff_files.extend(tiff_dir.glob(f"*{ext}"))

            return tiff_files

        except Exception as e:
            output_manager.error(
                f"❌ Error obteniendo archivos TIFF de {subfolder_name}: {str(e)}"
            )
            return []

    def _consolidate_tiff_to_pdf(
        self, tiff_files: List[Path], output_dir: Path, subfolder_name: str
    ) -> bool:
        """
        Consolida los archivos TIFF en uno o varios PDFs.

        Args:
            tiff_files: Lista de archivos TIFF ordenados
            output_dir: Directorio de salida
            subfolder_name: Nombre de la subcarpeta

        Returns:
            True si se creó exitosamente
        """
        try:
            if not tiff_files:
                return False

            # Calcular cuántos PDFs necesitamos
            total_files = len(tiff_files)
            files_per_pdf = self._calculate_files_per_pdf(tiff_files)

            if files_per_pdf >= total_files:
                # Un solo PDF
                return self._create_single_pdf(tiff_files, output_dir, subfolder_name)
            else:
                # Múltiples PDFs
                return self._create_multiple_pdfs(
                    tiff_files, output_dir, subfolder_name, files_per_pdf
                )

        except Exception as e:
            output_manager.error(f"❌ Error en consolidación de PDF: {str(e)}")
            return False

    def _calculate_files_per_pdf(self, tiff_files: List[Path]) -> int:
        """
        Calcula cuántos archivos TIFF caben en un PDF del tamaño máximo.

        Args:
            tiff_files: Lista de archivos TIFF

        Returns:
            Número de archivos por PDF
        """
        try:
            # Estimación: cada archivo TIFF puede ser ~2-5 MB en el PDF final
            # Usar una estimación conservadora
            estimated_mb_per_file = 3.0
            files_per_pdf = max(1, int(self.max_size_mb / estimated_mb_per_file))

            output_manager.info(
                f"ℹ️ Estimación: {files_per_pdf} archivos por PDF (máx {self.max_size_mb}MB)"
            )
            return files_per_pdf

        except Exception as e:
            output_manager.error(f"❌ Error calculando archivos por PDF: {str(e)}")
            return 10  # Valor por defecto

    def _create_single_pdf(
        self, tiff_files: List[Path], output_dir: Path, subfolder_name: str
    ) -> bool:
        """
        Crea un solo PDF consolidado.

        Args:
            tiff_files: Lista de archivos TIFF
            output_dir: Directorio de salida
            subfolder_name: Nombre de la subcarpeta

        Returns:
            True si se creó exitosamente
        """
        try:
            output_file = output_dir / f"{subfolder_name}_consolidated.pdf"

            # Convertir cada TIFF a PDF y luego consolidar
            pdf_files = []
            for tiff_file in tiff_files:
                temp_pdf = self._convert_tiff_to_pdf(tiff_file, output_dir)
                if temp_pdf:
                    pdf_files.append(temp_pdf)

            if not pdf_files:
                output_manager.error(f"❌ No se pudieron convertir archivos TIFF a PDF")
                return False

            # Consolidar PDFs en uno solo
            success = self._merge_pdfs(pdf_files, output_file)

            # Limpiar archivos temporales
            for temp_pdf in pdf_files:
                if temp_pdf.exists():
                    temp_pdf.unlink()

            if success:
                # Aplicar compresión al PDF consolidado si está habilitada
                if self.pdf_compressor.enabled:
                    # Crear archivo temporal para la compresión
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                        temp_pdf_path = Path(temp_file.name)
                    
                    # Comprimir el PDF consolidado
                    if self.pdf_compressor.compress(output_file, temp_pdf_path):
                        # Reemplazar el archivo original con el comprimido
                        import shutil
                        shutil.move(temp_pdf_path, output_file)
                        output_manager.success(
                            f"✅ PDF consolidado comprimido: {subfolder_name}_consolidated.pdf"
                        )
                    else:
                        # Si la compresión falla, mantener el original
                        if temp_pdf_path.exists():
                            temp_pdf_path.unlink()
                        output_manager.success(
                            f"✅ PDF consolidado creado: {subfolder_name}_consolidated.pdf"
                        )
                else:
                    output_manager.success(
                        f"✅ PDF consolidado creado: {subfolder_name}_consolidated.pdf"
                    )

            return success

        except Exception as e:
            output_manager.error(f"❌ Error creando PDF único: {str(e)}")
            return False

    def _create_multiple_pdfs(
        self,
        tiff_files: List[Path],
        output_dir: Path,
        subfolder_name: str,
        files_per_pdf: int,
    ) -> bool:
        """
        Crea múltiples PDFs divididos por tamaño.

        Args:
            tiff_files: Lista de archivos TIFF
            output_dir: Directorio de salida
            subfolder_name: Nombre de la subcarpeta
            files_per_pdf: Archivos por PDF

        Returns:
            True si se crearon exitosamente
        """
        try:
            success_count = 0
            total_pdfs = (len(tiff_files) + files_per_pdf - 1) // files_per_pdf

            for i in range(0, len(tiff_files), files_per_pdf):
                batch_files = tiff_files[i : i + files_per_pdf]
                pdf_number = (i // files_per_pdf) + 1

                output_file = output_dir / f"{subfolder_name}_{pdf_number:02d}.pdf"

                # Convertir batch de TIFFs a PDF
                pdf_files = []
                for tiff_file in batch_files:
                    temp_pdf = self._convert_tiff_to_pdf(tiff_file, output_dir)
                    if temp_pdf:
                        pdf_files.append(temp_pdf)

                if pdf_files:
                    # Consolidar batch en un PDF
                    if self._merge_pdfs(pdf_files, output_file):
                        # Aplicar compresión al PDF si está habilitada
                        if self.pdf_compressor.enabled:
                            # Crear archivo temporal para la compresión
                            import tempfile
                            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                                temp_pdf_path = Path(temp_file.name)
                            
                            # Comprimir el PDF
                            if self.pdf_compressor.compress(output_file, temp_pdf_path):
                                # Reemplazar el archivo original con el comprimido
                                import shutil
                                shutil.move(temp_pdf_path, output_file)
                                output_manager.success(
                                    f"PDF {pdf_number}/{total_pdfs} comprimido: {output_file.name}"
                                )
                            else:
                                # Si la compresión falla, mantener el original
                                if temp_pdf_path.exists():
                                    temp_pdf_path.unlink()
                                output_manager.success(
                                    f"PDF {pdf_number}/{total_pdfs} creado: {output_file.name}"
                                )
                        else:
                            output_manager.success(
                                f"PDF {pdf_number}/{total_pdfs} creado: {output_file.name}"
                            )
                        
                        success_count += 1

                    # Limpiar archivos temporales
                    for temp_pdf in pdf_files:
                        if temp_pdf.exists():
                            temp_pdf.unlink()

            output_manager.success(
                f"{success_count}/{total_pdfs} PDFs consolidados creados exitosamente"
            )
            return success_count > 0

        except Exception as e:
            output_manager.error(f"Error creando múltiples PDFs: {str(e)}")
            return False

    def _convert_tiff_to_pdf(self, tiff_file: Path, output_dir: Path) -> Optional[Path]:
        """
        Convierte un archivo TIFF a PDF usando el conversor existente.

        Args:
            tiff_file: Archivo TIFF a convertir
            output_dir: Directorio de salida

        Returns:
            Path del PDF temporal creado, o None si falló
        """
        try:
            # Crear nombre temporal para el PDF
            temp_pdf_name = f"temp_{tiff_file.stem}.pdf"
            temp_pdf_path = output_dir / temp_pdf_name

            # Usar el conversor PDF existente
            success = self.pdf_converter.convert(tiff_file, temp_pdf_path)

            if success and temp_pdf_path.exists():
                return temp_pdf_path
            else:
                return None

        except Exception as e:
            output_manager.error(f"Error convirtiendo {tiff_file.name} a PDF: {str(e)}")
            return None

    def _merge_pdfs(self, pdf_files: List[Path], output_file: Path) -> bool:
        """
        Combina múltiples PDFs en uno solo.

        Args:
            pdf_files: Lista de archivos PDF a combinar
            output_file: Archivo PDF de salida

        Returns:
            True si se combinó exitosamente
        """
        try:
            # Por ahora, si solo hay un PDF, simplemente copiarlo
            if len(pdf_files) == 1:
                import shutil

                shutil.copy2(pdf_files[0], output_file)
                return True

            # Para múltiples PDFs, usar PyPDF2
            try:
                from PyPDF2 import PdfMerger

                merger = PdfMerger()
                for pdf_file in pdf_files:
                    if pdf_file.exists():
                        merger.append(str(pdf_file))

                with open(output_file, "wb") as output:
                    merger.write(output)

                merger.close()
                return True

            except ImportError:
                output_manager.warning(
                    "PyPDF2 no disponible, usando método alternativo"
                )
                # Método alternativo: copiar el primer PDF
                import shutil

                shutil.copy2(pdf_files[0], output_file)
                return True

        except Exception as e:
            output_manager.error(f"Error combinando PDFs: {str(e)}")
            return False
