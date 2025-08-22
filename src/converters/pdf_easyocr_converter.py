"""
Conversor de imágenes TIFF a formato PDF con EasyOCR
Alternativa a Tesseract para reconocimiento de texto
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image
import easyocr
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import numpy as np
import time
from .base import BaseConverter


class PDFEasyOCRConverter(BaseConverter):
    """Conversor de TIFF a PDF con EasyOCR"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Valores por defecto para PDF
        self.resolution = config.get('resolution', 300)
        self.page_size = config.get('page_size', 'A4')
        self.fit_to_page = config.get('fit_to_page', True)
        
        # Configuración OCR
        self.ocr_language = config.get('ocr_language', ['es', 'en'])  # Lista de idiomas
        self.ocr_confidence = config.get('ocr_confidence', 0.5)  # Confianza (0.0-1.0)
        self.create_searchable_pdf = config.get('create_searchable_pdf', True)
        self.use_gpu = config.get('use_gpu', False)  # Usar GPU si está disponible
        
        # Inicializar EasyOCR
        self.reader = None
        self._initialize_easyocr()
    
    def _initialize_easyocr(self) -> None:
        """Inicializa EasyOCR con los idiomas especificados"""
        try:
            print(f"🔍 Inicializando EasyOCR para idiomas: {self.ocr_language}")
            
            # Configurar parámetros de EasyOCR
            gpu = self.use_gpu
            if not gpu:
                print("   ⚠️  GPU no habilitada, usando CPU (más lento)")
            
            # Inicializar lector
            self.reader = easyocr.Reader(
                self.ocr_language,
                gpu=gpu,
                model_storage_directory=None,  # Usar directorio por defecto
                download_enabled=True,  # Descargar modelos si no están disponibles
                verbose=False
            )
            
            print(f"✅ EasyOCR inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error inicializando EasyOCR: {str(e)}")
            print("   El PDF se creará sin OCR. Verifica la instalación de EasyOCR.")
            self.create_searchable_pdf = False
    
    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Convierte una imagen TIFF a PDF con OCR
        
        Args:
            input_path: Ruta del archivo TIFF de entrada
            output_path: Ruta del archivo PDF de salida
            
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
                
                # Ajustar resolución si es necesario
                if self.resolution != 300:
                    dpi_factor = self.resolution / 300
                    new_size = tuple(int(dim * dpi_factor) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Crear PDF con OCR si está habilitado
                if self.create_searchable_pdf and self.reader:
                    success = self._create_pdf_with_easyocr(img, output_path)
                else:
                    success = self._create_simple_pdf(img, output_path)
                
                if success:
                    print(f"Convertido: {input_path.name} -> {output_path.name}")
                    if self.create_searchable_pdf and self.reader:
                        print(f"  ✅ PDF con EasyOCR creado (idiomas: {self.ocr_language})")
                    else:
                        print(f"  📄 PDF simple creado")
                
                return success
                
        except Exception as e:
            print(f"Error convirtiendo {input_path.name} a PDF con EasyOCR: {str(e)}")
            return False
    
    def _create_simple_pdf(self, img: Image.Image, output_path: Path) -> bool:
        """Crea un PDF simple sin OCR"""
        try:
            img.save(output_path, 'PDF', resolution=self.resolution)
            return True
        except Exception as e:
            print(f"Error creando PDF simple: {str(e)}")
            return False
    
    def _create_pdf_with_easyocr(self, img: Image.Image, output_path: Path) -> bool:
        """Crea un PDF con EasyOCR para hacer el texto buscable"""
        try:
            # Crear PDF temporal con la imagen
            temp_pdf_path = output_path.with_suffix('.temp.pdf')
            img.save(temp_pdf_path, 'PDF', resolution=self.resolution)
            
            # Realizar OCR con EasyOCR
            print(f"🔍 Realizando OCR con EasyOCR en {img.size[0]}x{img.size[1]} píxeles...")
            start_time = time.time()
            
            # Convertir imagen a array numpy para EasyOCR
            img_array = np.array(img)
            
            # Realizar OCR
            results = self.reader.readtext(
                img_array,
                detail=1,  # Obtener detalles completos
                paragraph=True,  # Agrupar texto en párrafos
                contrast_ths=0.1,  # Umbral de contraste
                adjust_contrast=0.5,  # Ajustar contraste
                width_ths=0.7,  # Umbral de ancho para agrupar texto
                height_ths=0.7,  # Umbral de altura para agrupar texto
                link_threshold=0.4,  # Umbral para vincular líneas
                low_text=0.4,  # Umbral de texto bajo
                canvas_size=2560,  # Tamaño del canvas
                mag_ratio=1.5  # Ratio de magnificación
            )
            
            ocr_time = time.time() - start_time
            print(f"⏱️  OCR completado en {ocr_time:.2f} segundos")
            
            # Procesar resultados de OCR
            if not results:
                print("⚠️  No se detectó texto con EasyOCR, creando PDF simple")
                temp_pdf_path.unlink()
                return self._create_simple_pdf(img, output_path)
            
            # Extraer texto y posiciones
            text_blocks = self._process_easyocr_results(results, img.size)
            
            if not text_blocks:
                print("⚠️  No se pudo procesar el texto de EasyOCR, creando PDF simple")
                temp_pdf_path.unlink()
                return self._create_simple_pdf(img, output_path)
            
            # Crear PDF con capa de texto invisible
            self._add_text_layer_to_pdf(temp_pdf_path, output_path, text_blocks, img.size)
            
            # Limpiar archivo temporal
            temp_pdf_path.unlink()
            
            print(f"📝 EasyOCR completado: {len(text_blocks)} bloques de texto detectados")
            return True
            
        except Exception as e:
            print(f"Error en EasyOCR: {str(e)}, creando PDF simple")
            # Fallback a PDF simple
            return self._create_simple_pdf(img, output_path)
    
    def _process_easyocr_results(self, results: List[Tuple], img_size: Tuple[int, int]) -> List[Dict]:
        """
        Procesa los resultados de EasyOCR para extraer texto y posiciones
        
        Args:
            results: Resultados de EasyOCR
            img_size: Tamaño de la imagen (ancho, alto)
            
        Returns:
            Lista de bloques de texto con posición y contenido
        """
        text_blocks = []
        
        for (bbox, text, confidence) in results:
            # Filtrar por confianza
            if confidence < self.ocr_confidence:
                continue
            
            # Filtrar texto muy corto o solo espacios
            if len(text.strip()) < 2:
                continue
            
            # Calcular posición relativa en la página
            # bbox es una lista de 4 puntos: [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            
            # Calcular posición central del texto
            center_x = sum(x_coords) / len(x_coords)
            center_y = sum(y_coords) / len(y_coords)
            
            # Convertir coordenadas de píxeles a puntos PDF (72 puntos = 1 pulgada)
            # Asumiendo que la imagen se ajusta a A4
            pdf_width, pdf_height = A4
            
            # Calcular factores de escala
            scale_x = pdf_width / img_size[0]
            scale_y = pdf_height / img_size[1]
            
            # Posición en el PDF
            pdf_x = center_x * scale_x
            pdf_y = pdf_height - (center_y * scale_y)  # Invertir Y para PDF
            
            text_blocks.append({
                'text': text.strip(),
                'confidence': confidence,
                'x': pdf_x,
                'y': pdf_y,
                'bbox': bbox
            })
        
        return text_blocks
    
    def _add_text_layer_to_pdf(self, temp_pdf_path: Path, output_path: Path, 
                               text_blocks: List[Dict], img_size: Tuple[int, int]) -> None:
        """Agrega una capa de texto invisible al PDF para hacerlo buscable"""
        try:
            # Leer PDF temporal
            with open(temp_pdf_path, 'rb') as temp_file:
                pdf_reader = PdfReader(temp_file)
                pdf_writer = PdfWriter()
                
                # Procesar cada página
                for page_num, page in enumerate(pdf_reader.pages):
                    # Crear capa de texto invisible
                    text_layer = self._create_text_layer_easyocr(text_blocks, page_num)
                    
                    # Agregar página con capa de texto
                    page.merge_page(text_layer)
                    pdf_writer.add_page(page)
                
                # Guardar PDF final
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                    
        except Exception as e:
            print(f"Error agregando capa de texto: {str(e)}")
            # Si falla, copiar el PDF temporal
            import shutil
            shutil.copy2(temp_pdf_path, output_path)
    
    def _create_text_layer_easyocr(self, text_blocks: List[Dict], page_num: int) -> object:
        """Crea una capa de texto invisible para el PDF usando resultados de EasyOCR"""
        try:
            # Crear canvas temporal
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            # Configurar texto invisible
            can.setFont("Helvetica", 1)  # Fuente muy pequeña
            can.setFillAlpha(0.01)  # Casi transparente
            
            # Agregar texto en las posiciones detectadas por EasyOCR
            for block in text_blocks:
                text = block['text']
                x = block['x']
                y = block['y']
                confidence = block['confidence']
                
                # Agregar texto en la posición exacta detectada
                can.drawString(x, y, text)
                
                # Agregar variaciones de posición para mejor búsqueda
                can.drawString(x + 1, y, text)  # Ligeramente desplazado
                can.drawString(x, y + 1, text)  # Ligeramente desplazado
                
                # Agregar texto con confianza para debugging (opcional)
                if confidence < 0.7:
                    can.drawString(x + 50, y, f"[{confidence:.2f}] {text}")
            
            can.save()
            packet.seek(0)
            
            # Convertir a objeto PDF
            from PyPDF2 import PdfReader
            text_pdf = PdfReader(packet)
            return text_pdf.pages[0]
            
        except Exception as e:
            print(f"Error creando capa de texto: {str(e)}")
            # Retornar página vacía
            from PyPDF2 import PdfReader
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.save()
            packet.seek(0)
            text_pdf = PdfReader(packet)
            return text_pdf.pages[0]
    
    def get_file_extension(self) -> str:
        """Retorna la extensión .pdf"""
        return '.pdf'
    
    def get_output_filename(self, input_path: Path, output_dir: Path) -> Path:
        """
        Genera el nombre del archivo de salida con indicador EasyOCR
        
        Args:
            input_path: Archivo de entrada
            output_dir: Directorio de salida
            
        Returns:
            Ruta del archivo de salida
        """
        stem = input_path.stem
        extension = self.get_file_extension()
        
        # Crear subdirectorio específico para este formato
        format_dir = output_dir / "pdf_easyocr"
        format_dir.mkdir(parents=True, exist_ok=True)
        
        if self.create_searchable_pdf and self.reader:
            return format_dir / f"{stem}_EasyOCR{extension}"
        else:
            return format_dir / f"{stem}{extension}"
