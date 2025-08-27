"""
Motor principal de conversión de archivos TIFF
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

from tqdm import tqdm

from .config_manager import ConfigManager
from .converters import (
    JPGResolutionConverter,
    METMetadataConverter,
    PDFEasyOCRConverter,
)
from .file_processor import FileProcessor
from .output_manager import output_manager
from .postconverters import METFormatPostConverter


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
        self.postconverters = self._initialize_postconverters()

    def _initialize_converters(self) -> Dict[str, Any]:
        """Inicializa todos los conversores disponibles"""
        converters = {}

        # JPG 400 DPI Converter
        if self.config_manager.is_format_enabled("jpg_400"):
            jpg_400_config = self.config_manager.get_format_config("jpg_400")
            converters["jpg_400"] = JPGResolutionConverter(jpg_400_config)

        # JPG 200 DPI Converter
        if self.config_manager.is_format_enabled("jpg_200"):
            jpg_200_config = self.config_manager.get_format_config("jpg_200")
            converters["jpg_200"] = JPGResolutionConverter(jpg_200_config)

        # PDF EasyOCR Converter
        if self.config_manager.is_format_enabled("pdf_easyocr"):
            pdf_easyocr_config = self.config_manager.get_format_config("pdf_easyocr")
            converters["pdf_easyocr"] = PDFEasyOCRConverter(pdf_easyocr_config)

        # MET Metadata Converter
        if self.config_manager.is_format_enabled("met_metadata"):
            met_metadata_config = self.config_manager.get_format_config("met_metadata")
            # Agregar configuración del nivel superior para MET
            met_metadata_config.update(self.config_manager.config.get("met_metadata", {}))
            converters["met_metadata"] = METMetadataConverter(met_metadata_config)

        output_manager.info(f"Conversores inicializados: {list(converters.keys())}")
        return converters

    def _initialize_postconverters(self) -> Dict[str, Any]:
        """Inicializa todos los postconversores disponibles"""
        postconverters = {}

        # MET Format PostConverter
        if self.config_manager.config.get("postconverters", {}).get("met_format", {}).get("enabled", False):
            met_format_config = self.config_manager.config.get("postconverters", {}).get("met_format", {})
            postconverters["met_format"] = METFormatPostConverter(met_format_config)

        if postconverters:
            output_manager.info(f"Postconversores inicializados: {list(postconverters.keys())}")
        else:
            output_manager.info("No hay postconversores habilitados")

        return postconverters

    def convert_directory(
        self,
        input_dir: str,
        output_dir: str,
        formats: Optional[List[str]] = None,
        max_workers: Optional[int] = None,
    ) -> Dict[str, Any]:
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
                    "success": False,
                    "error": "No se encontraron archivos TIFF en el directorio de entrada",
                    "files_processed": 0,
                    "conversions_successful": 0,
                    "conversions_failed": 0,
                    "time_elapsed": 0,
                }

            # Filtrar formatos si se especifican
            if formats:
                available_formats = list(self.converters.keys())
                formats = [f for f in formats if f in available_formats]
                if not formats:
                    error_msg = (
                    f"No hay conversores disponibles para los formatos especificados: {formats}"
                )
                    return {
                        "success": False,
                        "error": error_msg,
                        "files_processed": 0,
                        "conversions_successful": 0,
                        "conversions_failed": 0,
                        "time_elapsed": 0,
                    }
            else:
                formats = list(self.converters.keys())

            # Crear estructura de salida
            output_config = self.config_manager.get_output_config()
            create_subdirs = output_config.get("create_subdirectories", True)
            file_processor.create_output_structure(create_subdirs)

            # Configuración de procesamiento
            processing_config = self.config_manager.get_processing_config()
            max_workers = max_workers or processing_config.get("max_workers", 4)
            overwrite = processing_config.get("overwrite_existing", False)

            output_manager.info(
                f"Procesando {len(tiff_files)} archivos TIFF a {len(formats)} formatos..."
            )
            output_manager.info(f"Usando {max_workers} workers en paralelo")

            # Estadísticas
            total_conversions = len(tiff_files) * len(formats)
            successful_conversions = 0
            failed_conversions = 0

            # Procesar archivos
            files_info = []  # Para almacenar información detallada de cada archivo
            
            # Crear barra de progreso principal
            with tqdm(
                total=total_conversions, 
                desc="Convirtiendo archivos",
                position=0,
                leave=True
            ) as main_pbar:
                # Configurar el gestor de salida
                output_manager.set_main_progress_bar(main_pbar)
                
                # Crear tareas
                future_to_task = {}
                
                # Usar ThreadPoolExecutor para procesamiento paralelo
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    for tiff_file in tiff_files:
                        for format_name in formats:
                            converter = self.converters[format_name]

                            # Usar método personalizado de nombre si está disponible
                            if hasattr(converter, "get_output_filename"):
                                output_path = converter.get_output_filename(
                                    tiff_file, file_processor.output_dir
                                )
                            else:
                                output_path = file_processor.get_output_path(
                                    tiff_file, format_name, create_subdirs
                                )

                            # Validar ruta de salida
                            if not file_processor.validate_output_path(
                                output_path, overwrite
                            ):
                                continue

                            # Enviar tarea al executor
                            future = executor.submit(
                                converter.convert, tiff_file, output_path
                            )
                            future_to_task[future] = (tiff_file.name, format_name)

                # Procesar resultados con barra de progreso
                for future in as_completed(future_to_task):
                    file_name, format_name = future_to_task[future]

                    try:
                        success = future.result()
                        if success:
                            successful_conversions += 1
                        else:
                            failed_conversions += 1
                    except Exception as e:
                        output_manager.error(
                            f"Error procesando {file_name} a {format_name}: {str(e)}"
                        )
                        failed_conversions += 1

                    main_pbar.update(1)
                    main_pbar.set_postfix(
                        {
                            "Exitosas": successful_conversions,
                            "Fallidas": failed_conversions,
                        }
                    )

            # Recopilar información detallada de los archivos procesados
            for tiff_file in tiff_files:
                file_info = {
                    "input_file": str(tiff_file),
                    "conversions": {}
                }
                
                for format_name in formats:
                    if format_name in self.converters:
                        converter = self.converters[format_name]
                        if hasattr(converter, "get_output_filename"):
                            output_path = converter.get_output_filename(
                                tiff_file, file_processor.output_dir
                            )
                        else:
                            output_path = file_processor.get_output_path(
                                tiff_file, format_name, create_subdirs
                            )
                        
                        # Verificar si el archivo existe (conversión exitosa)
                        if output_path.exists():
                            file_info["conversions"][format_name] = {
                                "success": True,
                                "output_path": str(output_path)
                            }
                        else:
                            file_info["conversions"][format_name] = {
                                "success": False,
                                "output_path": str(output_path)
                            }
                
                files_info.append(file_info)

            # Calcular tiempo total
            time_elapsed = time.time() - start_time

            # Resumen final
            result = {
                "success": True,
                "files_processed": len(tiff_files),
                "formats_processed": formats,
                "conversions_successful": successful_conversions,
                "conversions_failed": failed_conversions,
                "total_conversions": total_conversions,
                "time_elapsed": round(time_elapsed, 2),
                "input_directory": input_dir,
                "output_directory": output_dir,
                "files_info": files_info # Incluir la información detallada
            }

            self._print_summary(result)

            # Generar archivos MET por formato si está habilitado
            met_metadata_enabled = (
                self.config_manager.is_format_enabled("met_metadata") or
                self.config_manager.config.get("met_metadata", {}).get("enabled", False)
            )
            if met_metadata_enabled:
                self._generate_format_specific_met(result, output_dir)

            return result

        except Exception as e:
            time_elapsed = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "files_processed": 0,
                "conversions_successful": 0,
                "conversions_failed": 0,
                "time_elapsed": round(time_elapsed, 2),
            }

    def _print_summary(self, result: Dict[str, Any]) -> None:
        """Imprime un resumen de la conversión"""
        output_manager.section("RESUMEN DE CONVERSIÓN")
        output_manager.separator()

        if result["success"]:
            output_manager.success("Conversión completada exitosamente")
            output_manager.format_info("📁 Archivos procesados", result['files_processed'])
            output_manager.format_list("🔄 Formatos procesados", result['formats_processed'])
            output_manager.format_info("✅ Conversiones exitosas", result['conversions_successful'])
            output_manager.format_info("❌ Conversiones fallidas", result['conversions_failed'])
            output_manager.format_info("⏱️  Tiempo total", f"{result['time_elapsed']} segundos")
            output_manager.format_info("📂 Directorio de entrada", result['input_directory'])
            output_manager.format_info("📂 Directorio de salida", result['output_directory'])

            # Información específica de los formatos
            if "jpg_400" in result["formats_processed"]:
                output_manager.info("🖼️  JPG 400 DPI: Alta resolución para impresión")
            if "jpg_200" in result["formats_processed"]:
                output_manager.info("🖼️  JPG 200 DPI: Resolución media para web")
            if "pdf_easyocr" in result["formats_processed"]:
                output_manager.info("📄 PDF con EasyOCR: Texto buscable y seleccionable")
            if "met_metadata" in result["formats_processed"]:
                output_manager.info("📋 MET Metadata: Archivos XML con metadatos detallados")
        else:
            output_manager.error(f"Error en la conversión: {result['error']}")

        output_manager.separator()

    def get_available_formats(self) -> List[str]:
        """Retorna la lista de formatos disponibles"""
        return list(self.converters.keys())

    def get_available_postconverters(self) -> List[str]:
        """Retorna la lista de postconversores disponibles"""
        return list(self.postconverters.keys())

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
            "name": converter.__class__.__name__,
            "format": format_name,
            "extension": converter.get_file_extension(),
            "config": converter.config,
        }

        # Información específica por tipo de conversor
        if hasattr(converter, "dpi"):
            info["dpi"] = converter.dpi
        if hasattr(converter, "quality"):
            info["quality"] = converter.quality
        if hasattr(converter, "ocr_language"):
            info["ocr_language"] = converter.ocr_language
            info["ocr_enabled"] = converter.create_searchable_pdf

        return info

    def reload_config(self) -> bool:
        """Recarga la configuración y reinicializa los conversores"""
        if self.config_manager.reload_config():
            self.converters = self._initialize_converters()
            return True
        return False

    def _generate_format_specific_met(
        self, result: Dict[str, Any], output_dir: Path
    ) -> None:
        """
        Genera archivos MET separados, uno por cada tipo de formato

        Args:
            result: Resultado de la conversión
            output_dir: Directorio de salida
        """
        try:
            if not result.get("success"):
                return

            # Ejecutar postconversores habilitados
            for postconverter_name, postconverter in self.postconverters.items():
                try:
                    output_manager.info(f"Ejecutando postconversor: {postconverter.get_name()}")
                    success = postconverter.process(result, output_dir)
                    if success:
                        output_manager.success(f"Postconversor {postconverter_name} ejecutado exitosamente")
                    else:
                        output_manager.warning(f"Postconversor {postconverter_name} tuvo problemas")
                except Exception as e:
                    output_manager.error(f"Error ejecutando postconversor {postconverter_name}: {str(e)}")

        except Exception as e:
            output_manager.error(f"Error ejecutando postconversores: {str(e)}")


def main():
    """Función main para ejecutar el conversor como módulo"""
    output_manager.section("🔧 CONVERSOR TIFF - MÓDULO PRINCIPAL")
    output_manager.separator("=", 40)

    try:
        converter = TIFFConverter()
        output_manager.success("Conversor inicializado correctamente")
        output_manager.format_info("📁 Formatos disponibles", converter.get_available_formats())
        output_manager.format_info("🔄 Postconversores disponibles", converter.get_available_postconverters())

        # Mostrar información de cada conversor
        for format_name in converter.get_available_formats():
            info = converter.get_converter_info(format_name)
            if info:
                output_manager.section(f"📋 {format_name.upper()}:")
                output_manager.format_info("   Clase", info['name'])
                output_manager.format_info("   Extensión", info['extension'])
                if "dpi" in info:
                    output_manager.format_info("   DPI", info['dpi'])
                if "quality" in info:
                    output_manager.format_info("   Calidad", info['quality'])
                if "ocr_language" in info:
                    output_manager.format_info("   OCR", info['ocr_language'])

        # Mostrar información de postconversores
        if converter.get_available_postconverters():
            output_manager.section("🔄 POSTCONVERSORES:")
            for postconverter_name in converter.get_available_postconverters():
                postconverter = converter.postconverters[postconverter_name]
                output_manager.format_info(f"   {postconverter_name}", postconverter.get_name())

        output_manager.section("💡 Para usar el conversor:")
        output_manager.info("   python main.py --input 'entrada' --output 'salida'")
        output_manager.info("   python main.py --info")

    except Exception as e:
        output_manager.error(f"Error: {str(e)}")
        return False

    return True


if __name__ == "__main__":
    main()
