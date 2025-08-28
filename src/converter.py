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
from .postconverters import ConsolidatedPDFPostconverter


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
        if self.config_manager.is_format_enabled("JPGHIGH"):
            jpg_400_config = self.config_manager.get_format_config("JPGHIGH")
            converters["JPGHIGH"] = JPGResolutionConverter(jpg_400_config)

        # JPG 200 DPI Converter
        if self.config_manager.is_format_enabled("JPGLOW"):
            jpg_200_config = self.config_manager.get_format_config("JPGLOW")
            converters["JPGLOW"] = JPGResolutionConverter(jpg_200_config)

        # PDF EasyOCR Converter
        if self.config_manager.is_format_enabled("PDF"):
            pdf_easyocr_config = self.config_manager.get_format_config("PDF")
            converters["PDF"] = PDFEasyOCRConverter(pdf_easyocr_config)

        # MET Metadata Converter
        if self.config_manager.is_format_enabled("METS"):
            met_metadata_config = self.config_manager.get_format_config("METS")
            # Agregar configuración del nivel superior para MET
            met_metadata_config.update(
                self.config_manager.config.get("METS", {})
            )
            converters["METS"] = METMetadataConverter(met_metadata_config)

        output_manager.info(f"Conversores inicializados: {list(converters.keys())}")
        return converters

    def _initialize_postconverters(self) -> Dict[str, Any]:
        """Inicializa todos los postconversores disponibles"""
        postconverters = {}

        # MET Format PostConverter
        if (
            self.config_manager.config.get("postconverters", {})
            .get("met_format", {})
            .get("enabled", False)
        ):
            met_format_config = self.config_manager.config.get(
                "postconverters", {}
            ).get("met_format", {})
            postconverters["met_format"] = METFormatPostConverter(met_format_config)

        # Consolidated PDF PostConverter
        if (
            self.config_manager.config.get("postconverters", {})
            .get("consolidated_pdf", {})
            .get("enabled", False)
        ):
            consolidated_pdf_config = self.config_manager.config.get(
                "postconverters", {}
            ).get("consolidated_pdf", {})
            postconverters["consolidated_pdf"] = ConsolidatedPDFPostconverter(consolidated_pdf_config)

        if postconverters:
            output_manager.info(
                f"Postconversores inicializados: {list(postconverters.keys())}"
            )
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
        Convierte todos los archivos TIFF de todas las subcarpetas que contengan carpetas TIFF

        Args:
            input_dir: Directorio de entrada raíz
            output_dir: Directorio de destino para las conversiones
            formats: Lista de formatos específicos a convertir (opcional)
            max_workers: Número máximo de workers para procesamiento paralelo

        Returns:
            Diccionario con estadísticas de la conversión por subcarpeta
        """
        start_time = time.time()

        try:
            # Inicializar procesador de archivos
            file_processor = FileProcessor(input_dir, output_dir)

            # Obtener carpetas TIFF encontradas
            tiff_folders = file_processor.get_tiff_folders()
            if not tiff_folders:
                return {
                    "success": False,
                    "error": "No se encontraron carpetas TIFF en el directorio de entrada",
                    "subfolders_processed": 0,
                    "total_files_processed": 0,
                    "time_elapsed": 0,
                }

            # Filtrar formatos si se especifican
            if formats:
                available_formats = list(self.converters.keys())
                formats = [f for f in formats if f in available_formats]
                if not formats:
                    error_msg = f"No hay conversores disponibles para los formatos especificados: {formats}"
                    return {
                        "success": False,
                        "error": error_msg,
                        "subfolders_processed": 0,
                        "total_files_processed": 0,
                        "time_elapsed": 0,
                    }
            else:
                formats = list(self.converters.keys())

            # Configuración de procesamiento
            processing_config = self.config_manager.get_processing_config()
            max_workers = max_workers or processing_config.get("max_workers", 1)
            overwrite = processing_config.get("overwrite_existing", False)

            output_manager.info(
                f"🚀 Procesando {len(tiff_folders)} subcarpetas con carpetas TIFF..."
            )
            output_manager.info(f"Formatos a convertir: {', '.join(formats)}")
            output_manager.info(f"Usando {max_workers} workers en paralelo")

            # Habilitar logging a archivo
            output_manager.enable_file_logging(output_dir)

            # Procesar cada subcarpeta
            subfolder_results = {}
            error_report = {}

            for subfolder_name, tiff_folder in tiff_folders.items():
                output_manager.section(f"📁 Procesando subcarpeta: {subfolder_name}")
                
                try:
                    # Crear estructura de salida para esta subcarpeta
                    if not file_processor.create_output_structure_for_subfolder(subfolder_name, formats):
                        error_report[subfolder_name] = [f"Error creando estructura de salida"]
                        continue

                    # Procesar archivos TIFF de esta subcarpeta
                    subfolder_result = self._process_subfolder(
                        file_processor, 
                        subfolder_name, 
                        tiff_folder, 
                        formats, 
                        max_workers, 
                        overwrite
                    )
                    
                    subfolder_results[subfolder_name] = subfolder_result
                    
                    # Ejecutar postconversores para esta subcarpeta
                    if subfolder_result.get("success") and self.postconverters:
                        self._run_postconverters_for_subfolder(
                            subfolder_result, 
                            output_dir, 
                            subfolder_name,
                            file_processor
                        )
                    
                    # Generar resumen de la subcarpeta
                    summary = file_processor.get_summary_by_subfolder().get(subfolder_name, {})
                    output_manager.log_subfolder_summary(subfolder_name, summary)
                    
                except Exception as e:
                    error_msg = f"Error procesando subcarpeta {subfolder_name}: {str(e)}"
                    output_manager.error(error_msg)
                    error_report[subfolder_name] = [error_msg]
                    continue

            # Generar reporte final
            time_elapsed = time.time() - start_time
            final_result = self._generate_final_result(
                subfolder_results, 
                error_report, 
                time_elapsed,
                file_processor
            )

            # Log del reporte de errores si los hay
            if error_report:
                output_manager.log_error_report(error_report)

            return final_result

        except Exception as e:
            output_manager.error(f"❌ Error inesperado en la conversión: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "subfolders_processed": 0,
                "total_files_processed": 0,
                "time_elapsed": time.time() - start_time,
            }

    def _process_subfolder(
        self,
        file_processor: FileProcessor,
        subfolder_name: str,
        tiff_folder: Path,
        formats: List[str],
        max_workers: int,
        overwrite: bool
    ) -> Dict[str, Any]:
        """
        Procesa una subcarpeta específica
        
        Args:
            file_processor: Procesador de archivos
            subfolder_name: Nombre de la subcarpeta
            tiff_folder: Ruta a la carpeta TIFF
            formats: Formatos a convertir
            max_workers: Número de workers
            overwrite: Si sobrescribir archivos
            
        Returns:
            Resultado del procesamiento de la subcarpeta
        """
        # Obtener archivos TIFF de esta subcarpeta
        tiff_files = file_processor.get_tiff_files_from_folder(tiff_folder)
        if not tiff_files:
            return {
                "success": False,
                "error": f"No se encontraron archivos TIFF en {subfolder_name}/TIFF/",
                "files_processed": 0,
                "conversions_successful": 0,
                "conversions_failed": 0,
            }

        output_manager.info(f"📄 Encontrados {len(tiff_files)} archivos TIFF en {subfolder_name}/TIFF/")

        # Estadísticas
        total_conversions = len(tiff_files) * len(formats)
        successful_conversions = 0
        failed_conversions = 0

        # Crear barra de progreso para esta subcarpeta
        with tqdm(
            total=total_conversions,
            desc=f"Convirtiendo {subfolder_name}",
            position=0,
            leave=True,
        ) as pbar:
            output_manager.set_main_progress_bar(pbar)

            # Procesar archivos
            for tiff_file in tiff_files:
                for format_name in formats:
                    converter = self.converters[format_name]

                    # Generar ruta de salida para esta subcarpeta
                    output_path = file_processor.get_output_path_for_subfolder(
                        tiff_file, format_name, subfolder_name
                    )

                    # Validar ruta de salida
                    if not file_processor.validate_output_path(output_path, overwrite):
                        pbar.update(1)
                        failed_conversions += 1
                        continue

                    # Convertir archivo
                    try:
                        success = converter.convert(tiff_file, output_path)
                        
                        if success:
                            successful_conversions += 1
                            # Agregar resultado para postconversores
                            file_processor.add_conversion_result(subfolder_name, {
                                "input_file": str(tiff_file),
                                "output_file": str(output_path),
                                "format": format_name,
                                "success": True,
                                "subfolder": subfolder_name
                            })
                        else:
                            failed_conversions += 1
                            file_processor.add_conversion_result(subfolder_name, {
                                "input_file": str(tiff_file),
                                "output_file": str(output_path),
                                "format": format_name,
                                "success": False,
                                "subfolder": subfolder_name
                            })
                        
                    except Exception as e:
                        failed_conversions += 1
                        output_manager.error(f"❌ Error convirtiendo {tiff_file.name} a {format_name}: {str(e)}")
                        file_processor.add_conversion_result(subfolder_name, {
                            "input_file": str(tiff_file),
                            "output_file": str(output_path),
                            "format": format_name,
                            "success": False,
                            "error": str(e),
                            "subfolder": subfolder_name
                        })

                    pbar.update(1)

        return {
            "success": True,
            "files_processed": len(tiff_files),
            "conversions_successful": successful_conversions,
            "conversions_failed": failed_conversions,
            "formats_processed": formats,
            "subfolder": subfolder_name
        }

    def _run_postconverters_for_subfolder(
        self,
        subfolder_result: Dict[str, Any],
        output_dir: str,
        subfolder_name: str,
        file_processor: FileProcessor
    ):
        """
        Ejecuta los postconversores para una subcarpeta específica
        
        Args:
            subfolder_result: Resultado del procesamiento de la subcarpeta
            output_dir: Directorio de salida
            subfolder_name: Nombre de la subcarpeta
            file_processor: Procesador de archivos
        """
        output_manager.info(f"🔄 Ejecutando postconversores para {subfolder_name}...")
        
        # Debug temporal: verificar el estado del file_processor
        conversion_results = file_processor.get_conversion_results()
        output_manager.info(f"Debug - file_processor.get_conversion_results(): {conversion_results}")
        
        for postconverter_name, postconverter in self.postconverters.items():
            try:
                # Crear resultado específico para esta subcarpeta
                subfolder_conversion_result = {
                    "success": True,
                    "files_info": file_processor.get_conversion_results().get(subfolder_name, []),
                    "subfolder": subfolder_name
                }
                
                # Ejecutar postconversor
                success = postconverter.process(subfolder_conversion_result, Path(output_dir))
                
                if success:
                    output_manager.success(f"✅ Postconversor {postconverter_name} completado para {subfolder_name}")
                else:
                    output_manager.error(f"❌ Postconversor {postconverter_name} falló para {subfolder_name}")
                    
            except Exception as e:
                output_manager.error(f"❌ Error en postconversor {postconverter_name} para {subfolder_name}: {str(e)}")

    def _generate_final_result(
        self,
        subfolder_results: Dict[str, Dict],
        error_report: Dict[str, List[str]],
        time_elapsed: float,
        file_processor: FileProcessor
    ) -> Dict[str, Any]:
        """
        Genera el resultado final de la conversión
        
        Args:
            subfolder_results: Resultados por subcarpeta
            error_report: Reporte de errores
            time_elapsed: Tiempo transcurrido
            file_processor: Procesador de archivos
            
        Returns:
            Resultado final consolidado
        """
        # Calcular estadísticas totales
        total_subfolders = len(subfolder_results) + len(error_report)
        successful_subfolders = len(subfolder_results)
        failed_subfolders = len([k for k, v in error_report.items() if v])
        
        total_files = sum(r.get("files_processed", 0) for r in subfolder_results.values())
        total_conversions = sum(r.get("conversions_successful", 0) for r in subfolder_results.values())
        total_failures = sum(r.get("conversions_failed", 0) for r in subfolder_results.values())

        # Generar resumen por subcarpeta
        summary_by_subfolder = file_processor.get_summary_by_subfolder()

        result = {
            "success": successful_subfolders > 0,
            "subfolders_processed": total_subfolders,
            "subfolders_successful": successful_subfolders,
            "subfolders_failed": failed_subfolders,
            "total_files_processed": total_files,
            "total_conversions_successful": total_conversions,
            "total_conversions_failed": total_failures,
            "time_elapsed": time_elapsed,
            "subfolder_results": subfolder_results,
            "error_report": error_report,
            "summary_by_subfolder": summary_by_subfolder
        }

        # Mostrar resumen final
        output_manager.section("📊 RESUMEN FINAL DE CONVERSIÓN")
        output_manager.separator()
        output_manager.format_info("📁 Subcarpetas procesadas", f"{successful_subfolders}/{total_subfolders}")
        output_manager.format_info("📄 Archivos totales", total_files)
        output_manager.format_info("✅ Conversiones exitosas", total_conversions)
        output_manager.format_info("❌ Conversiones fallidas", total_failures)
        output_manager.format_info("⏱️  Tiempo total", f"{time_elapsed:.2f} segundos")

        if error_report:
            output_manager.warning(f"⚠️  {failed_subfolders} subcarpetas tuvieron errores")
            output_manager.info("📋 Revisa el archivo de log para detalles completos")

        return result

    def get_available_formats(self) -> List[str]:
        """Retorna la lista de formatos disponibles"""
        return list(self.converters.keys())

    def get_available_postconverters(self) -> List[str]:
        """Retorna la lista de postconversores disponibles"""
        return list(self.postconverters.keys())

    def get_converter_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Retorna información de un conversor específico"""
        if format_name in self.converters:
            converter = self.converters[format_name]
            info = converter.get_converter_info()
            
            # Agregar información específica del formato
            if format_name == "JPGHIGH":
                info.update({"dpi": 400, "quality": converter.quality})
            elif format_name == "JPGLOW":
                info.update({"dpi": 200, "quality": converter.quality})
            elif format_name == "PDF":
                info.update({"ocr_language": converter.ocr_language})
            
            return info
        return None

    def reload_config(self) -> bool:
        """Recarga la configuración y reinicializa los conversores"""
        if self.config_manager.reload_config():
            self.converters = self._initialize_converters()
            return True
        return False


def main():
    """Función main para ejecutar el conversor como módulo"""
    output_manager.section("🔧 CONVERSOR TIFF - MÓDULO PRINCIPAL")
    output_manager.separator("=", 40)

    try:
        converter = TIFFConverter()
        output_manager.success("Conversor inicializado correctamente")
        output_manager.format_info(
            "📁 Formatos disponibles", converter.get_available_formats()
        )
        output_manager.format_info(
            "🔄 Postconversores disponibles", converter.get_available_postconverters()
        )

        # Mostrar información de cada conversor
        for format_name in converter.get_available_formats():
            info = converter.get_converter_info(format_name)
            if info:
                output_manager.section(f"📋 {format_name.upper()}:")
                output_manager.format_info("   Clase", info["name"])
                output_manager.format_info("   Extensión", info["extension"])
                if "dpi" in info:
                    output_manager.format_info("   DPI", info["dpi"])
                if "quality" in info:
                    output_manager.format_info("   Calidad", info["quality"])
                if "ocr_language" in info:
                    output_manager.format_info("   OCR", info["ocr_language"])

        # Mostrar información de postconversores
        if converter.get_available_postconverters():
            output_manager.section("🔄 POSTCONVERSORES:")
            for postconverter_name in converter.get_available_postconverters():
                postconverter = converter.postconverters[postconverter_name]
                output_manager.format_info(
                    f"   {postconverter_name}", postconverter.get_name()
                )

        output_manager.section("💡 Para usar el conversor:")
        output_manager.info("   python main.py --input 'entrada' --output 'salida'")
        output_manager.info("   python main.py --info")

    except Exception as e:
        output_manager.error(f"Error: {str(e)}")
        return False

    return True


if __name__ == "__main__":
    main()
