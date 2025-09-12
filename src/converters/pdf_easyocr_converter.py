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
from .pdf_compressor import PDFCompressor


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
        self.use_ocr = config.get("use_ocr", True)  # Nueva opción para controlar OCR
        self.page_size = config.get("page_size", "A4")
        self.fit_to_page = config.get("fit_to_page", True)
        self.ocr_confidence = config.get("ocr_confidence", 0.5)
        self.ocr_reader = None
        # Configuración de compresión
        compression_config = config.get("compression", {})
        self.pdf_compressor = PDFCompressor(compression_config)
        # Parámetros de incrustación en PDF (100% Python)
        # Si hay valores en compression, los usamos; si no, caemos a defaults del conversor
        self.embed_target_dpi = compression_config.get(
            "target_dpi", config.get("resolution", 300)
        )
        self.embed_image_quality = compression_config.get("image_quality", 85)
        
        # Solo inicializar EasyOCR si está habilitado
        if self.use_ocr and self.create_searchable_pdf:
            self._initialize_easyocr()
        else:
            output_manager.info("ℹ️ OCR deshabilitado - PDFs se crearán sin texto buscable")
            self.ocr_reader = None

    def _initialize_easyocr(self) -> None:
        """Inicializa EasyOCR con el idioma especificado"""
        try:
            if isinstance(self.ocr_language, str):
                languages = [self.ocr_language]
            elif isinstance(self.ocr_language, list):
                languages = self.ocr_language
            else:
                languages = ["es"]  # Fallback a español
                output_manager.warning("⚠️ Formato de idioma OCR inválido, usando español por defecto")

            output_manager.info(f"Inicializando EasyOCR con idioma: {languages[0]}")
            # Usar GPU si está configurado y disponible
            use_gpu = self.config.get("use_gpu", False)
            self.ocr_reader = easyocr.Reader(languages, gpu=use_gpu)
            output_manager.success("✅ EasyOCR inicializado correctamente")

        except ImportError:
            output_manager.error("❌ EasyOCR no está instalado. Instalar con: pip install easyocr")
            self.ocr_reader = None
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
            # LOG DETALLADO: Inicio de conversión
            output_manager.info(f"🔄 [PDF] INICIANDO CONVERSIÓN")
            output_manager.info(f"📁 [PDF] Ruta entrada: {input_path.absolute()}")
            output_manager.info(f"📁 [PDF] Ruta salida: {output_path.absolute()}")
            output_manager.info(f"📊 [PDF] Tamaño entrada: {input_path.stat().st_size / (1024*1024):.2f} MB")
            output_manager.info(f"🔧 [PDF] OCR habilitado: {self.use_ocr}")
            output_manager.info(f"🔧 [PDF] PDF buscable: {self.create_searchable_pdf}")
            output_manager.info(f"🔧 [PDF] EasyOCR disponible: {self.ocr_reader is not None}")
            
            # Validar entrada
            output_manager.info(f"🔍 [PDF] Validando archivo de entrada...")
            if not self.validate_input(input_path):
                output_manager.error(
                    f"❌ [PDF] Error: Archivo de entrada inválido: {input_path.absolute()}"
                )
                return False
            output_manager.info(f"✅ [PDF] Archivo de entrada válido")

            # Crear directorio de salida
            output_manager.info(f"📂 [PDF] Creando directorio de salida: {output_path.parent.absolute()}")
            if not self.create_output_directory(output_path):
                output_manager.error(
                    f"❌ [PDF] Error: No se pudo crear el directorio de salida: {output_path.parent.absolute()}"
                )
                return False
            output_manager.info(f"✅ [PDF] Directorio de salida creado")

            # Verificar que EasyOCR esté disponible solo si OCR está habilitado
            if self.use_ocr and self.create_searchable_pdf and not self.ocr_reader:
                output_manager.error("❌ [PDF] EasyOCR no está disponible pero OCR está habilitado")
                return False

            # Crear PDF con OCR
            output_manager.info(f"🔄 [PDF] Iniciando creación de PDF con OCR...")
            success = self._create_pdf_with_easyocr(input_path, output_path)
            
            if success:
                output_manager.info(f"✅ [PDF] PDF creado exitosamente")
                
                # Aplicar compresión si está habilitada
                if self.pdf_compressor.config['enabled']:
                    output_manager.info(f"🗜️ [PDF] Iniciando compresión de PDF...")
                    # Crear archivo temporal para la compresión
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                        temp_pdf_path = Path(temp_file.name)
                    
                    output_manager.info(f"📁 [PDF] Archivo temporal: {temp_pdf_path.absolute()}")
                    
                    # Comprimir el PDF
                    if self.pdf_compressor.compress(output_path, temp_pdf_path):
                        output_manager.info(f"✅ [PDF] Compresión exitosa")
                        # Reemplazar el archivo original con el comprimido
                        import shutil
                        shutil.move(temp_pdf_path, output_path)
                        output_manager.info(f"✅ [PDF] Archivo comprimido reemplazado")
                    else:
                        output_manager.warning(f"⚠️ [PDF] Compresión falló, manteniendo original")
                        # Si la compresión falla, mantener el original
                        if temp_pdf_path.exists():
                            temp_pdf_path.unlink()
                else:
                    output_manager.info(f"ℹ️ [PDF] Compresión deshabilitada")
                
                # Log final de éxito
                final_size = output_path.stat().st_size / (1024*1024)
                output_manager.success(
                    f"✅ [PDF] CONVERSIÓN COMPLETADA: {input_path.name} -> {output_path.name} ({final_size:.2f} MB)"
                )
                return success
            else:
                output_manager.error(f"❌ [PDF] Error en la creación del PDF")
                return False

        except Exception as e:
            output_manager.error(f"❌ [PDF] ERROR CRÍTICO convirtiendo {input_path.name}: {str(e)}")
            output_manager.error(f"❌ [PDF] Tipo de error: {type(e).__name__}")
            import traceback
            output_manager.error(f"❌ [PDF] Traceback: {traceback.format_exc()}")
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
            output_manager.info(f"🔄 [PDF-OCR] Abriendo imagen TIFF...")
            # Abrir imagen TIFF con PIL
            with Image.open(input_path) as pil_img:
                output_manager.info(f"✅ [PDF-OCR] Imagen abierta: {pil_img.size[0]}x{pil_img.size[1]} px, modo: {pil_img.mode}")
                
                # Convertir a RGB si es necesario
                if pil_img.mode not in ["RGB", "L"]:
                    output_manager.info(f"🔄 [PDF-OCR] Convirtiendo de {pil_img.mode} a RGB...")
                    pil_img = pil_img.convert("RGB")
                    output_manager.info(f"✅ [PDF-OCR] Conversión completada")

                # Obtener dimensiones
                img_width, img_height = pil_img.size
                output_manager.info(f"📊 [PDF-OCR] Dimensiones originales: {img_width}x{img_height} píxeles")
                
                # Reducir tamaño de imagen para OCR si es muy grande
                max_ocr_size = 2048  # Máximo 2048 píxeles para OCR
                if img_width > max_ocr_size or img_height > max_ocr_size:
                    output_manager.info(f"🔄 [PDF-OCR] Imagen muy grande para OCR, redimensionando...")
                    # Calcular factor de escala manteniendo proporción
                    scale_factor = min(max_ocr_size / img_width, max_ocr_size / img_height)
                    new_width = int(img_width * scale_factor)
                    new_height = int(img_height * scale_factor)
                    
                    pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    output_manager.info(f"✅ [PDF-OCR] Imagen redimensionada: {new_width}x{new_height} píxeles")
                    
                    # Actualizar dimensiones
                    img_width, img_height = pil_img.size

                # Crear PDF con tamaño exacto de la imagen (sin bordes)
                # Convertir píxeles a puntos (1 punto = 1/72 pulgada)
                # Usar DPI configurable para controlar tamaño del PDF resultante
                dpi = int(self.embed_target_dpi) if self.embed_target_dpi else 300
                points_per_inch = 72
                scale_factor = points_per_inch / dpi

                page_width = img_width * scale_factor
                page_height = img_height * scale_factor
                
                output_manager.info(f"📏 [PDF-OCR] DPI objetivo: {dpi}")
                output_manager.info(f"📏 [PDF-OCR] Factor de escala: {scale_factor:.4f}")
                output_manager.info(f"📏 [PDF-OCR] Tamaño página PDF: {page_width:.2f}x{page_height:.2f} puntos")

                # Crear PDF con tamaño personalizado
                output_manager.info(f"🔄 [PDF-OCR] Creando canvas PDF...")
                canvas_obj = reportlab_canvas.Canvas(
                    str(output_path), pagesize=(page_width, page_height)
                )
                output_manager.info(f"✅ [PDF-OCR] Canvas PDF creado")

                # Sin escalado, usar tamaño original
                scale = 1.0
                x = 0
                y = 0

                # Crear archivo temporal para ReportLab
                import os
                import tempfile

                output_manager.info(f"🔄 [PDF-OCR] Creando archivo temporal JPEG...")
                with tempfile.NamedTemporaryFile(
                    suffix=".jpg", delete=False
                ) as temp_file:
                    # Guardar como JPEG con calidad configurable para reducir tamaño
                    # optimize True ayuda a reducir ligeramente el tamaño
                    pil_img.save(
                        temp_file.name,
                        format="JPEG",
                        quality=int(self.embed_image_quality),
                        optimize=True,
                    )            # Agregar imagen al PDF ocupando toda la página
                    canvas_obj.drawImage(temp_file.name, x, y, page_width, page_height)

                # Limpiar archivo temporal
                os.unlink(temp_file.name)

                # Realizar OCR si está habilitado
                if self.use_ocr and self.create_searchable_pdf and self.ocr_reader:
                    self._add_text_layer_to_pdf(canvas_obj, pil_img, scale, x, y)
                elif not self.use_ocr:
                    output_manager.info(f"ℹ️ OCR deshabilitado para {input_path.name} - PDF sin texto buscable")

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
                "use_ocr": self.use_ocr,
                "page_size": self.page_size,
                "fit_to_page": self.fit_to_page,
                "ocr_confidence": self.ocr_confidence,
                "format": "PDF",
            }
        )
        return base_info
