"""
Motor principal de conversión de archivos TIFF
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

from tqdm import tqdm

from .config_manager import ConfigManager
from .file_processor import FileProcessor
from .converters import JPGResolutionConverter, PDFEasyOCRConverter, METMetadataConverter


class TIFFConverter:
    """Motor principal de conversión de archivos TIFF"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa el conversor principal

        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.config_manager = ConfigManager(config_path)
        self.converters = self._initialize_converters()

    def _initialize_converters(self) -> Dict[str, Any]:
        """Inicializa todos los conversores disponibles"""
        converters = {}

        # JPG 400 DPI Converter
        if self.config_manager.is_format_enabled('jpg_400'):
            jpg_400_config = self.config_manager.get_format_config('jpg_400')
            converters['jpg_400'] = JPGResolutionConverter(jpg_400_config)

        # JPG 200 DPI Converter
        if self.config_manager.is_format_enabled('jpg_200'):
            jpg_200_config = self.config_manager.get_format_config('jpg_200')
            converters['jpg_200'] = JPGResolutionConverter(jpg_200_config)

        # PDF EasyOCR Converter
        if self.config_manager.is_format_enabled('pdf_easyocr'):
            pdf_easyocr_config = self.config_manager.get_format_config('pdf_easyocr')
            converters['pdf_easyocr'] = PDFEasyOCRConverter(pdf_easyocr_config)

        # MET Metadata Converter
        if self.config_manager.is_format_enabled('met_metadata'):
            met_metadata_config = self.config_manager.get_format_config('met_metadata')
            converters['met_metadata'] = METMetadataConverter(met_metadata_config)

        print(f"Conversores inicializados: {list(converters.keys())}")
        return converters

    def convert_directory(self, input_dir: str, output_dir: str,
                         formats: Optional[List[str]] = None,
                         max_workers: Optional[int] = None) -> Dict[str, Any]:
        """
        Convierte todos los archivos TIFF de un directorio

        Args:
            input_dir: Directorio de entrada con archivos TIFF
            output_dir: Directorio de destino para las conversiones
            formats: Lista de formatos específicos a convertir (opcional)
            max_workers: Número máximo de workers para procesamiento paralelo

        Returns:
            Diccionario con estadísticas de la conversión
        """
        start_time = time.time()

        try:
            # Inicializar procesador de archivos
            file_processor = FileProcessor(input_dir, output_dir)

            # Obtener archivos TIFF
            tiff_files = file_processor.get_tiff_files()
            if not tiff_files:
                return {
                    'success': False,
                    'error': 'No se encontraron archivos TIFF en el directorio de entrada',
                    'files_processed': 0,
                    'conversions_successful': 0,
                    'conversions_failed': 0,
                    'time_elapsed': 0
                }

            # Filtrar formatos si se especifican
            if formats:
                available_formats = list(self.converters.keys())
                formats = [f for f in formats if f in available_formats]
                if not formats:
                    error_msg = (
                        f'No hay conversores disponibles para los formatos especificados: {formats}'
                    )
                    return {
                        'success': False,
                        'error': error_msg,
                        'files_processed': 0,
                        'conversions_successful': 0,
                        'conversions_failed': 0,
                        'time_elapsed': 0
                    }
            else:
                formats = list(self.converters.keys())

            # Crear estructura de salida
            output_config = self.config_manager.get_output_config()
            create_subdirs = output_config.get('create_subdirectories', True)
            file_processor.create_output_structure(create_subdirs)

            # Configuración de procesamiento
            processing_config = self.config_manager.get_processing_config()
            max_workers = max_workers or processing_config.get('max_workers', 4)
            overwrite = processing_config.get('overwrite_existing', False)

            print(f"Procesando {len(tiff_files)} archivos TIFF a {len(formats)} formatos...")
            print(f"Usando {max_workers} workers en paralelo")

            # Estadísticas
            total_conversions = len(tiff_files) * len(formats)
            successful_conversions = 0
            failed_conversions = 0

            # Procesar archivos
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Crear tareas
                future_to_task = {}

                for tiff_file in tiff_files:
                    for format_name in formats:
                        converter = self.converters[format_name]

                        # Usar método personalizado de nombre si está disponible
                        if hasattr(converter, 'get_output_filename'):
                            output_path = converter.get_output_filename(
                                tiff_file, file_processor.output_dir
                            )
                        else:
                            output_path = file_processor.get_output_path(
                                tiff_file, format_name, create_subdirs
                            )

                        # Validar ruta de salida
                        if not file_processor.validate_output_path(output_path, overwrite):
                            continue

                        # Enviar tarea al executor
                        future = executor.submit(
                            converter.convert, tiff_file, output_path
                        )
                        future_to_task[future] = (tiff_file.name, format_name)

                # Procesar resultados con barra de progreso
                with tqdm(total=total_conversions, desc="Convirtiendo archivos") as pbar:
                    for future in as_completed(future_to_task):
                        file_name, format_name = future_to_task[future]

                        try:
                            success = future.result()
                            if success:
                                successful_conversions += 1
                            else:
                                failed_conversions += 1
                        except Exception as e:
                            print(f"Error procesando {file_name} a {format_name}: {str(e)}")
                            failed_conversions += 1

                        pbar.update(1)
                        pbar.set_postfix({
                            'Exitosas': successful_conversions,
                            'Fallidas': failed_conversions
                        })

            # Calcular tiempo total
            time_elapsed = time.time() - start_time

            # Resumen final
            result = {
                'success': True,
                'files_processed': len(tiff_files),
                'formats_processed': formats,
                'conversions_successful': successful_conversions,
                'conversions_failed': failed_conversions,
                'total_conversions': total_conversions,
                'time_elapsed': round(time_elapsed, 2),
                'input_directory': input_dir,
                'output_directory': output_dir
            }

            self._print_summary(result)
            return result

        except Exception as e:
            time_elapsed = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'files_processed': 0,
                'conversions_successful': 0,
                'conversions_failed': 0,
                'time_elapsed': round(time_elapsed, 2)
            }

    def _print_summary(self, result: Dict[str, Any]) -> None:
        """Imprime un resumen de la conversión"""
        print("\n" + "="*50)
        print("RESUMEN DE CONVERSIÓN")
        print("="*50)

        if result['success']:
            print("✅ Conversión completada exitosamente")
            print(f"📁 Archivos procesados: {result['files_processed']}")
            print(f"🔄 Formatos procesados: {', '.join(result['formats_processed'])}")
            print(f"✅ Conversiones exitosas: {result['conversions_successful']}")
            print(f"❌ Conversiones fallidas: {result['conversions_failed']}")
            print(f"⏱️  Tiempo total: {result['time_elapsed']} segundos")
            print(f"📂 Directorio de entrada: {result['input_directory']}")
            print(f"📂 Directorio de salida: {result['output_directory']}")

            # Información específica de los formatos
            if 'jpg_400' in result['formats_processed']:
                print("🖼️  JPG 400 DPI: Alta resolución para impresión")
            if 'jpg_200' in result['formats_processed']:
                print("🖼️  JPG 200 DPI: Resolución media para web")
            if 'pdf_easyocr' in result['formats_processed']:
                print("📄 PDF con EasyOCR: Texto buscable y seleccionable")
            if 'met_metadata' in result['formats_processed']:
                print("📋 MET Metadata: Archivos XML con metadatos detallados")
        else:
            print(f"❌ Error en la conversión: {result['error']}")

        print("="*50)

    def get_available_formats(self) -> List[str]:
        """Retorna la lista de formatos disponibles"""
        return list(self.converters.keys())

    def get_converter_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un conversor específico

        Args:
            format_name: Nombre del formato

        Returns:
            Información del conversor o None si no existe
        """
        if format_name not in self.converters:
            return None

        converter = self.converters[format_name]
        info = {
            'name': converter.__class__.__name__,
            'format': format_name,
            'extension': converter.get_file_extension(),
            'config': converter.config
        }

        # Información específica por tipo de conversor
        if hasattr(converter, 'dpi'):
            info['dpi'] = converter.dpi
        if hasattr(converter, 'quality'):
            info['quality'] = converter.quality
        if hasattr(converter, 'ocr_language'):
            info['ocr_language'] = converter.ocr_language
            info['ocr_enabled'] = converter.create_searchable_pdf

        return info

    def reload_config(self) -> bool:
        """Recarga la configuración y reinicializa los conversores"""
        if self.config_manager.reload_config():
            self.converters = self._initialize_converters()
            return True
        return False


def main():
    """Función main para ejecutar el conversor como módulo"""
    print("🔧 CONVERSOR TIFF - MÓDULO PRINCIPAL")
    print("=" * 40)

    try:
        converter = TIFFConverter()
        print("✅ Conversor inicializado correctamente")
        print(f"📁 Formatos disponibles: {converter.get_available_formats()}")

        # Mostrar información de cada conversor
        for format_name in converter.get_available_formats():
            info = converter.get_converter_info(format_name)
            if info:
                print(f"\n📋 {format_name.upper()}:")
                print(f"   Clase: {info['name']}")
                print(f"   Extensión: {info['extension']}")
                if 'dpi' in info:
                    print(f"   DPI: {info['dpi']}")
                if 'ocr_language' in info:
                    print(f"   OCR: {info['ocr_language']}")

        print("\n💡 Para usar el conversor:")
        print("   python main.py --input 'entrada' --output 'salida'")
        print("   python main.py --info")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    return True


if __name__ == '__main__':
    main()
