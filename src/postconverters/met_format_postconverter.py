"""
Postconversor que genera archivos MET por tipo de formato
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..output_manager import output_manager
from .base import BasePostConverter


class METFormatPostConverter(BasePostConverter):
    """Postconversor que genera archivos MET por tipo de formato"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el postconversor MET por formato

        Args:
            config: Configuración del postconversor
        """
        super().__init__(config)
        self.include_image_metadata = config.get("include_image_metadata", True)
        self.include_file_metadata = config.get("include_file_metadata", True)
        self.include_processing_info = config.get("include_processing_info", True)
        self.metadata_standard = config.get("metadata_standard", "MET")
        self.organization = config.get("organization", "Conversor TIFF")
        self.creator = config.get("creator", "Sistema Automatizado")

    def get_name(self) -> str:
        """Retorna el nombre del postconversor"""
        return "MET Format PostConverter"

    def process(self, conversion_result: Dict[str, Any], output_dir: Path) -> bool:
        """
        Procesa el resultado de la conversión y genera archivos MET por formato

        Args:
            conversion_result: Resultado de la conversión principal
            output_dir: Directorio de salida

        Returns:
            True si el procesamiento fue exitoso
        """
        try:
            if not conversion_result.get("success"):
                output_manager.warning("No se puede procesar conversión fallida")
                return False

            # Preparar los resultados para los archivos MET por formato
            conversion_results = self._prepare_conversion_results(conversion_result)

            # Generar archivos MET por formato
            results = self._create_format_specific_met(conversion_results, output_dir)

            # Mostrar resumen de generación
            successful_formats = [
                fmt for fmt, success in results.items() if success
            ]
            failed_formats = [
                fmt for fmt, success in results.items() if not success
            ]

            if successful_formats:
                output_manager.success(
                    f"Archivos MET generados para: {', '.join(successful_formats)}"
                )
            if failed_formats:
                output_manager.error(f"Errores generando MET para: {', '.join(failed_formats)}")

            return len(failed_formats) == 0

        except Exception as e:
            output_manager.error(f"Error en postconversor MET: {str(e)}")
            return False

    def _prepare_conversion_results(self, conversion_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prepara los resultados de conversión para la generación de MET

        Args:
            conversion_result: Resultado de la conversión principal

        Returns:
            Lista de resultados preparados
        """
        conversion_results = []

        for file_info in conversion_result.get("files_info", []):
            input_file = Path(file_info["input_file"])
            output_files = []

            # Agregar información de cada formato generado
            for format_name in conversion_result.get("formats_processed", []):
                if format_name in file_info.get("conversions", {}):
                    conversion = file_info["conversions"][format_name]
                    if conversion.get("success"):
                        output_path = Path(conversion["output_path"])
                        try:
                            size = output_path.stat().st_size if output_path.exists() else 0
                        except (OSError, FileNotFoundError):
                            size = 0
                        output_files.append(
                            {
                                "format": format_name,
                                "path": output_path,
                                "size": size,
                            }
                        )

            conversion_results.append(
                {
                    "input_file": input_file,
                    "output_files": output_files,
                    "success": len(output_files) > 0,
                }
            )

        return conversion_results

    def _create_format_specific_met(
        self, conversion_results: List[Dict[str, Any]], output_dir: Path
    ) -> Dict[str, bool]:
        """
        Crea archivos MET específicos para cada formato

        Args:
            conversion_results: Resultados de conversión preparados
            output_dir: Directorio de salida

        Returns:
            Diccionario con el resultado por formato
        """
        results = {}

        # Agrupar archivos por formato
        files_by_format = {}
        for result in conversion_results:
            if result["success"]:
                for output_file in result["output_files"]:
                    format_type = output_file["format"]
                    if format_type not in files_by_format:
                        files_by_format[format_type] = []
                    
                    # Debug: verificar el tipo de datos del tamaño
                    size_value = output_file["size"]
                    output_manager.info(f"Debug - Formato: {format_type}, Tamaño: {size_value} (tipo: {type(size_value)})")
                    
                    files_by_format[format_type].append({
                        "input_file": result["input_file"],
                        "output_file": {
                            "path": output_file["path"],
                            "size": size_value
                        }
                    })

        # Generar archivo MET para cada formato
        for format_type, files in files_by_format.items():
            try:
                success = self._create_single_format_met_file(format_type, files, output_dir)
                results[format_type] = success
            except Exception as e:
                output_manager.error(f"Error generando archivo MET para {format_type}: {str(e)}")
                results[format_type] = False

        return results

    def _create_single_format_met_file(
        self, format_type: str, files: List[Dict[str, Any]], output_dir: Path
    ) -> bool:
        """
        Crea un archivo XML MET único para un formato con nombre fijo

        Args:
            format_type: Tipo de formato (jpg_400, pdf_easyocr, etc.)
            files: Lista de archivos del formato
            output_dir: Directorio de salida

        Returns:
            True si se creó correctamente
        """
        try:
            # Crear elemento raíz MET
            root = ET.Element("mets")
            root.set("xmlns", "http://www.loc.gov/METS/")
            root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
            root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            root.set(
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
                "http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd"
            )

            # Agregar información del objeto
            objid = ET.SubElement(root, "objid")
            objid.text = f"MET_{format_type.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Agregar información del agente
            agent = ET.SubElement(root, "agent")
            agent.set("ROLE", "CREATOR")
            agent.set("TYPE", "ORGANIZATION")
            name = ET.SubElement(agent, "name")
            name.text = self.organization

            # Agregar información de creación
            creation_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            mets_hdr = ET.SubElement(root, "metsHdr")
            mets_hdr.set("CREATEDATE", creation_date)
            mets_hdr.set("LASTMODDATE", creation_date)
            agent_hdr = ET.SubElement(mets_hdr, "agent")
            agent_hdr.set("ROLE", "CREATOR")
            agent_hdr.set("TYPE", "OTHER")
            agent_hdr.set("OTHERTYPE", "SOFTWARE")
            name_hdr = ET.SubElement(agent_hdr, "name")
            name_hdr.text = self.creator

            # Agregar sección de archivos
            file_sec = ET.SubElement(root, "fileSec")
            file_grp = ET.SubElement(file_sec, "fileGrp")
            file_grp.set("USE", format_type.upper())
            file_grp.set("ID", f"FILEGRP_{format_type.upper()}")

            # Agregar cada archivo del formato
            for file_info in files:
                file_elem = ET.SubElement(file_grp, "file")
                file_elem.set(
                    "ID", f"FILE_{file_info['input_file'].stem}_{format_type}"
                )
                file_elem.set("MIMETYPE", self._get_mime_type(format_type))
                try:
                    size_value = int(file_info["output_file"]["size"])
                    file_elem.set("SIZE", str(size_value))
                except (ValueError, TypeError):
                    file_elem.set("SIZE", "0")

                # Agregar metadatos del archivo original
                if self.include_file_metadata:
                    input_path = Path(file_info["input_file"])
                    self._add_file_metadata(file_elem, input_path)

                # Agregar metadatos de imagen si es aplicable
                if self.include_image_metadata and format_type in [
                    "jpg_400",
                    "jpg_200",
                ]:
                    input_path = Path(file_info["input_file"])
                    self._add_image_metadata(file_elem, input_path)

                # Ubicación del archivo de salida
                flocat = ET.SubElement(file_elem, "FLocat")
                href_value = str(file_info["output_file"]["path"].absolute())
                flocat.set("{http://www.w3.org/1999/xlink}href", href_value)

            # Agregar sección de metadatos administrativos con tab premis
            amd_sec = ET.SubElement(root, "amdSec")
            premis_md = ET.SubElement(amd_sec, "premisMD")
            premis_md.set("ID", f"PREMIS_{format_type.upper()}")

            md_wrap = ET.SubElement(premis_md, "mdWrap")
            md_wrap.set("MDTYPE", "PREMIS")
            md_wrap.set("OTHERMDTYPE", "PREMIS")

            xml_data = ET.SubElement(md_wrap, "xmlData")

            # Crear estructura PREMIS
            premis_root = ET.SubElement(xml_data, "premis")
            premis_root.set("xmlns", "http://www.loc.gov/premis/v3")
            premis_root.set("version", "3.0")

            # Agregar objetos (archivos)
            objects_elem = ET.SubElement(premis_root, "objects")
            for file_info in files:
                object_elem = ET.SubElement(objects_elem, "object")
                # Simplificar para evitar problemas de namespace
                # object_elem.set("{http://www.w3.org/2001/XMLSchema-instance}type", "representation")

                # Identificador del objeto
                object_id = ET.SubElement(object_elem, "objectIdentifier")
                object_id_value = ET.SubElement(object_id, "objectIdentifierValue")
                object_id_value.text = f"{file_info['input_file'].stem}_{format_type}"
                object_id_type = ET.SubElement(object_id, "objectIdentifierType")
                object_id_type.text = "LOCAL"

                # Características del objeto
                object_characteristics = ET.SubElement(
                    object_elem, "objectCharacteristics"
                )

                # Tamaño
                size_elem = ET.SubElement(object_characteristics, "size")
                try:
                    size_value = int(file_info["output_file"]["size"])
                    size_elem.text = str(size_value)
                except (ValueError, TypeError):
                    size_elem.text = "0"

                # Formato
                format_elem = ET.SubElement(object_characteristics, "format")
                format_designation = ET.SubElement(format_elem, "formatDesignation")
                format_name = ET.SubElement(format_designation, "formatName")
                format_name.text = format_type

                # Creación
                creation_elem = ET.SubElement(object_characteristics, "creation")
                creation_date_elem = ET.SubElement(creation_elem, "dateCreated")
                creation_date_elem.text = creation_date

            # Crear y guardar el archivo XML con nombre fijo
            filename = f"{format_type}.xml"
            output_path = output_dir / filename

            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(output_path, encoding="utf-8", xml_declaration=True)

            return True

        except Exception as e:
            output_manager.error(f"Error creando archivo MET único para {format_type}: {str(e)}")
            return False

    def _add_file_metadata(self, file_elem: ET.Element, input_path: Path) -> None:
        """
        Agrega metadatos del archivo al elemento MET

        Args:
            file_elem: Elemento file del MET
            input_path: Ruta del archivo de entrada
        """
        try:
            stat = input_path.stat()

            # Información del archivo
            file_info = ET.SubElement(file_elem, "fileInfo")
            file_info.set("name", input_path.name)
            file_info.set("extension", input_path.suffix)
            file_info.set("size_bytes", str(stat.st_size))
            try:
                size_mb = f"{stat.st_size / (1024 * 1024):.2f}"
                file_info.set("size_mb", size_mb)
            except (TypeError, ValueError):
                file_info.set("size_mb", "0.00")
            created_time = datetime.fromtimestamp(stat.st_ctime).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            file_info.set("created", created_time)
            modified_time = datetime.fromtimestamp(stat.st_mtime).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            file_info.set("modified", modified_time)
            accessed_time = datetime.fromtimestamp(stat.st_atime).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            file_info.set("accessed", accessed_time)

            # Información de permisos
            permissions = oct(stat.st_mode)[-3:]
            file_info.set("permissions", permissions)

        except Exception as e:
            output_manager.error(f"Error obteniendo metadatos del archivo: {str(e)}")

    def _add_image_metadata(self, file_elem: ET.Element, input_path: Path) -> None:
        """
        Agrega metadatos de imagen al elemento MET

        Args:
            file_elem: Elemento file del MET
            input_path: Ruta del archivo de entrada
        """
        try:
            from PIL import Image

            with Image.open(input_path) as img:
                # Información de imagen
                img_info = ET.SubElement(file_elem, "imageInfo")
                img_info.set("width", str(img.width))
                img_info.set("height", str(img.height))
                img_info.set("mode", img.mode)
                img_info.set("format", img.format or "TIFF")

                # Información de DPI si está disponible
                if hasattr(img, "info") and "dpi" in img.info:
                    dpi_x, dpi_y = img.info["dpi"]
                    img_info.set("dpi_x", str(dpi_x))
                    img_info.set("dpi_y", str(dpi_y))

                # Orientación si está disponible
                if hasattr(img, "getexif"):
                    try:
                        exif = img.getexif()
                        if exif:
                            orientation = exif.get(274)  # Orientation tag
                            if orientation:
                                orientation_values = {
                                    1: "Normal",
                                    2: "Mirror horizontal",
                                    3: "Rotate 180",
                                    4: "Mirror vertical",
                                    5: "Mirror horizontal and rotate 270 CW",
                                    6: "Rotate 90 CW",
                                    7: "Mirror horizontal and rotate 90 CW",
                                    8: "Rotate 270 CW"
                                }
                                orientation_value = orientation_values.get(orientation, "Unknown")
                                img_info.set("orientation", orientation_value)
                    except Exception as easyocr_error:
                        output_manager.error(f"Error obteniendo metadatos de imagen: {str(easyocr_error)}")
                        pass

        except Exception as e:
            output_manager.error(f"Error obteniendo metadatos de imagen: {str(e)}")

    def _get_mime_type(self, format_type: str) -> str:
        """
        Retorna el MIME type correspondiente al formato

        Args:
            format_type: Tipo de formato

        Returns:
            MIME type correspondiente
        """
        mime_types = {
            "jpg_400": "image/jpeg",
            "jpg_200": "image/jpeg",
            "pdf_easyocr": "application/pdf",
            "met_metadata": "application/xml",
        }
        return mime_types.get(format_type, "application/octet-stream")
