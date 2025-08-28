"""
Conversor de TIFF a PDF con OCR usando EasyOCR
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import easyocr
import numpy as np
from PIL import Image

from reportlab.pdfgen import canvas as reportlab_canvas

from ..output_manager import output_manager
from .base import BaseConverter


class PDFEasyOCRConverter(BaseConverter):
    """Conversor de TIFF a PDF con OCR usando EasyOCR"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el conversor PDF con EasyOCR

        Args:
            config: Configuración del conversor
        """
        super().__init__(config)
        self.ocr_language = config.get("ocr_language", ["es"])
        self.create_searchable_pdf = config.get("create_searchable_pdf", True)
        self.page_size = config.get("page_size", "A4")
        self.fit_to_page = config.get("fit_to_page", True)
        self.ocr_confidence = config.get("ocr_confidence", 0.5)
        self.ocr_reader = None
        self._initialize_easyocr()

    def _initialize_easyocr(self) -> None:
        """Inicializa EasyOCR con el idioma especificado"""
        try:
            if isinstance(self.ocr_language, str):
                languages = [self.ocr_language]
            else:
                languages = self.ocr_language

            output_manager.info(f"Inicializando EasyOCR con idioma: {languages[0]}")
            # Usar GPU si está configurado y disponible
            use_gpu = self.config.get("use_gpu", False)
            self.ocr_reader = easyocr.Reader(languages, gpu=use_gpu)
            output_manager.success("✅ EasyOCR inicializado correctamente")

        except Exception as e:
            output_manager.error(f"❌ Error inicializando EasyOCR: {str(e)}")
            self.ocr_reader = None

    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Convierte un archivo TIFF a PDF con OCR

        Args:
            input_path: Ruta del archivo TIFF de entrada
            output_path: Ruta del archivo PDF de salida

        Returns:
            True si la conversión fue exitosa
        """
        try:
            # Validar entrada
            if not self.validate_input(input_path):
                output_manager.error(
                    f"Error: Archivo de entrada inválido: {input_path}"
                )
                return False

            # Crear directorio de salida
            if not self.create_output_directory(output_path):
                output_manager.error(
                    f"Error: No se pudo crear el directorio de salida: {output_path.parent}"
                )
                return False

            # Verificar que EasyOCR esté disponible
            if not self.ocr_reader:
                output_manager.error("❌ EasyOCR no está disponible")
                return False

            # Crear PDF con OCR
            success = self._create_pdf_with_easyocr(input_path, output_path)
            if success:
                output_manager.success(
                    f"✅ Convertido: {input_path.name} -> {output_path.name}"
                )
            return success

        except Exception as e:
            output_manager.error(f"❌ Error convirtiendo {input_path.name}: {str(e)}")
            return False

    def _create_pdf_with_easyocr(self, input_path: Path, output_path: Path) -> bool:
        """
        Crea un PDF con OCR usando EasyOCR

        Args:
            input_path: Archivo TIFF de entrada
            output_path: Archivo PDF de salida

        Returns:
            True si se creó correctamente
        """
        try:
            # Abrir imagen TIFF con PIL
            with Image.open(input_path) as pil_img:
                # Convertir a RGB si es necesario
                if pil_img.mode not in ["RGB", "L"]:
                    pil_img = pil_img.convert("RGB")

                # Obtener dimensiones
                img_width, img_height = pil_img.size

                # Crear PDF con tamaño exacto de la imagen (sin bordes)
                # Convertir píxeles a puntos (1 punto = 1/72 pulgada)
                # Asumiendo 300 DPI para la conversión
                dpi = 300
                points_per_inch = 72
                scale_factor = points_per_inch / dpi

                page_width = img_width * scale_factor
                page_height = img_height * scale_factor

                # Crear PDF con tamaño personalizado
                canvas_obj = reportlab_canvas.Canvas(
                    str(output_path), pagesize=(page_width, page_height)
                )

                # Sin escalado, usar tamaño original
                scale = 1.0
                x = 0
                y = 0

                # Crear archivo temporal para ReportLab
                import os
                import tempfile

                with tempfile.NamedTemporaryFile(
                    suffix=".jpg", delete=False
                ) as temp_file:
                    pil_img.save(temp_file.name, format="JPEG", quality=95)
                    # Agregar imagen al PDF ocupando toda la página
                    canvas_obj.drawImage(temp_file.name, x, y, page_width, page_height)

                # Limpiar archivo temporal
                os.unlink(temp_file.name)

                # Realizar OCR si está habilitado
                if self.create_searchable_pdf:
                    self._add_text_layer_to_pdf(canvas_obj, pil_img, scale, x, y)

                canvas_obj.save()

            return True

        except Exception as e:
            output_manager.error(f"Error creando PDF: {str(e)}")
            return False

    def _add_text_layer_to_pdf(
        self,
        canvas: reportlab_canvas.Canvas,
        img: Image.Image,
        scale: float,
        offset_x: float,
        offset_y: float,
    ) -> None:
        """
        Agrega una capa de texto invisible al PDF basada en OCR

        Args:
            canvas: Canvas de ReportLab
            img: Imagen PIL
            scale: Factor de escala aplicado
            offset_x: Desplazamiento X (siempre 0 ahora)
            offset_y: Desplazamiento Y (siempre 0 ahora)
        """
        try:
            # Convertir imagen PIL a array numpy para EasyOCR
            img_array = np.array(img)

            # Realizar OCR en la imagen
            ocr_results = self.ocr_reader.readtext(img_array)

            # Procesar resultados del OCR
            text_elements = self._process_easyocr_results(ocr_results, img.height)

            # Agregar texto invisible al PDF
            for text_element in text_elements:
                self._create_text_layer_easyocr(canvas, text_element)

        except Exception as e:
            output_manager.error(f"Error agregando capa de texto: {str(e)}")

    def _process_easyocr_results(
        self, results: List[Tuple], img_height: int
    ) -> List[Dict]:
        """
        Procesa los resultados de EasyOCR para extraer texto y posiciones

        Args:
            results: Resultados del OCR de EasyOCR
            img_height: Altura de la imagen en píxeles

        Returns:
            Lista de elementos de texto procesados
        """
        text_elements = []

        for bbox, text, confidence in results:
            if confidence >= self.ocr_confidence:
                # Extraer coordenadas del bbox
                points = np.array(bbox)
                x_coords = points[:, 0]
                y_coords = points[:, 1]

                # Calcular posición en el PDF
                # Convertir coordenadas de imagen a coordenadas de PDF
                dpi = 300
                points_per_inch = 72
                scale_factor = points_per_inch / dpi

                pdf_x = min(x_coords) * scale_factor
                # Invertir coordenada Y (ReportLab usa coordenadas desde abajo)
                pdf_y = (img_height - max(y_coords)) * scale_factor

                # Calcular dimensiones del texto
                width = (max(x_coords) - min(x_coords)) * scale_factor
                height = (max(y_coords) - min(y_coords)) * scale_factor

                text_elements.append(
                    {
                        "text": text,
                        "x": pdf_x,
                        "y": pdf_y,
                        "width": width,
                        "height": height,
                        "confidence": confidence,
                    }
                )

        return text_elements

    def _create_text_layer_easyocr(
        self, canvas: reportlab_canvas.Canvas, text_element: Dict
    ) -> None:
        """
        Crea una capa de texto invisible en el PDF

        Args:
            canvas: Canvas de ReportLab
            text_element: Elemento de texto a agregar
        """
        try:
            # Configurar fuente invisible (transparente)
            canvas.setFont("Helvetica", 8)
            canvas.setFillAlpha(0.0)  # Completamente transparente

            # Agregar texto en la posición calculada
            canvas.drawString(
                text_element["x"], text_element["y"], text_element["text"]
            )

        except Exception as e:
            output_manager.error(f"Error creando capa de texto: {str(e)}")

    def get_file_extension(self) -> str:
        """Retorna la extensión del archivo PDF"""
        return ".pdf"

    def get_output_filename(self, input_path: Path, output_dir: Path) -> Path:
        """
        Genera el nombre del archivo de salida con subdirectorio específico

        Args:
            input_path: Archivo de entrada
            output_dir: Directorio base de salida

        Returns:
            Ruta completa del archivo de salida
        """
        # Crear subdirectorio específico para este formato
        format_subdir = output_dir / "PDF"
        format_subdir.mkdir(exist_ok=True)

        stem = input_path.stem
        extension = self.get_file_extension()
        filename = f"{stem}{extension}"
        return format_subdir / filename

    def get_converter_info(self) -> Dict[str, Any]:
        """
        Retorna información específica del conversor PDF

        Returns:
            Diccionario con información del conversor
        """
        base_info = super().get_converter_info()
        base_info.update(
            {
                "ocr_language": self.ocr_language,
                "create_searchable_pdf": self.create_searchable_pdf,
                "page_size": self.page_size,
                "fit_to_page": self.fit_to_page,
                "ocr_confidence": self.ocr_confidence,
                "format": "PDF",
            }
        )
        return base_info
