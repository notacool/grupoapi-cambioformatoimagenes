"""
Conversor de TIFF a PDF con OCR usando EasyOCR
"""

import io
from pathlib import Path
from typing import Any, Dict, List, Tuple

import easyocr
import numpy as np
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas

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
        self.ocr_language = config.get("ocr_language", "es")
        self.create_searchable_pdf = config.get("create_searchable_pdf", True)
        self.page_size = config.get("page_size", "A4")
        self.fit_to_page = config.get("fit_to_page", True)
        self.ocr_confidence = config.get("ocr_confidence", 0.5)
        self.ocr_reader = None
        self._initialize_easyocr()

    def _initialize_easyocr(self) -> None:
        """Inicializa el lector de EasyOCR"""
        try:
            print(f"Inicializando EasyOCR con idioma: {self.ocr_language}")
            self.ocr_reader = easyocr.Reader([self.ocr_language])
            print("✅ EasyOCR inicializado correctamente")
        except Exception as e:
            print(f"❌ Error inicializando EasyOCR: {str(e)}")
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
                print(f"Error: Archivo de entrada inválido: {input_path}")
                return False

            # Crear directorio de salida
            if not self.create_output_directory(output_path):
                print(
                    f"Error: No se pudo crear el directorio de salida: {output_path.parent}"
                )
                return False

            # Verificar que EasyOCR esté disponible
            if not self.ocr_reader:
                print("❌ EasyOCR no está disponible")
                return False

            # Crear PDF con OCR
            success = self._create_pdf_with_easyocr(input_path, output_path)
            if success:
                print(f"✅ Convertido: {input_path.name} -> {output_path.name}")
            return success

        except Exception as e:
            print(f"❌ Error convirtiendo {input_path.name}: {str(e)}")
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
            # Abrir imagen TIFF
            with Image.open(input_path) as img:
                # Convertir a RGB si es necesario
                if img.mode not in ["RGB", "L"]:
                    img = img.convert("RGB")

                # Obtener dimensiones
                img_width, img_height = img.size

                # Crear PDF con ReportLab
                canvas = Canvas(str(output_path), pagesize=A4)
                page_width, page_height = A4

                # Calcular escala para ajustar a la página
                if self.fit_to_page:
                    scale_x = page_width / img_width
                    scale_y = page_height / img_height
                    scale = min(scale_x, scale_y) * 0.9  # 90% para márgenes
                else:
                    scale = 1.0

                # Calcular posición centrada
                scaled_width = img_width * scale
                scaled_height = img_height * scale
                x = (page_width - scaled_width) / 2
                y = (page_height - scaled_height) / 2

                # Convertir imagen a bytes para ReportLab
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=95)
                img_bytes.seek(0)

                # Agregar imagen al PDF
                canvas.drawImage(img_bytes, x, y, scaled_width, scaled_height)

                # Realizar OCR si está habilitado
                if self.create_searchable_pdf:
                    self._add_text_layer_to_pdf(canvas, img, scale, x, y)

                canvas.save()

            return True

        except Exception as e:
            print(f"Error creando PDF: {str(e)}")
            return False

    def _add_text_layer_to_pdf(
        self, canvas: Canvas, img: Image.Image, scale: float, x: float, y: float
    ) -> None:
        """
        Agrega una capa de texto invisible al PDF basada en OCR

        Args:
            canvas: Canvas de ReportLab
            img: Imagen PIL
            scale: Factor de escala aplicado
            x: Posición X en el PDF
            y: Posición Y en el PDF
        """
        try:
            # Realizar OCR en la imagen
            ocr_results = self.ocr_reader.readtext(np.array(img))

            # Procesar resultados del OCR
            text_elements = self._process_easyocr_results(ocr_results, scale, x, y)

            # Agregar texto invisible al PDF
            for text_element in text_elements:
                self._create_text_layer_easyocr(canvas, text_element)

        except Exception as e:
            print(f"Error agregando capa de texto: {str(e)}")

    def _process_easyocr_results(
        self, results: List[Tuple], scale: float, offset_x: float, offset_y: float
    ) -> List[Dict]:
        """
        Procesa los resultados de EasyOCR para extraer texto y posiciones

        Args:
            results: Resultados del OCR de EasyOCR
            scale: Factor de escala
            offset_x: Desplazamiento X
            offset_y: Desplazamiento Y

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
                pdf_x = min(x_coords) * scale + offset_x
                pdf_y = A4[1] - (max(y_coords) * scale + offset_y)

                # Calcular dimensiones del texto
                width = (max(x_coords) - min(x_coords)) * scale
                height = (max(y_coords) - min(y_coords)) * scale

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

    def _create_text_layer_easyocr(self, canvas: Canvas, text_element: Dict) -> None:
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
            print(f"Error creando capa de texto: {str(e)}")

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
        format_subdir = output_dir / "pdf_easyocr"
        format_subdir.mkdir(exist_ok=True)

        stem = input_path.stem
        extension = self.get_file_extension()
        filename = f"{stem}_EasyOCR{extension}"
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
