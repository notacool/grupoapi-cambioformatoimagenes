"""
Postconversor que genera archivos MET por tipo de formato y un archivo METS del TIFF original
"""

import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..output_manager import output_manager
from .base import BasePostConverter


class METFormatPostConverter(BasePostConverter):
    """Postconversor que genera archivos MET por tipo de formato y un archivo METS del TIFF original"""

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
        y un archivo METS del TIFF original para la subcarpeta específica

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

            # Obtener el nombre de la subcarpeta
            subfolder_name = conversion_result.get("subfolder", "unknown")

            # Preparar los resultados para los archivos MET por formato
            conversion_results = self._prepare_conversion_results(conversion_result)

            # Generar archivos MET por formato para esta subcarpeta
            results = self._create_format_specific_met_for_subfolder(
                conversion_results, output_dir, subfolder_name
            )

            # Mostrar resumen de generación
            successful_formats = [
                fmt
                for fmt, success in results.items()
                if success and fmt != "original_tiff_mets"
            ]
            failed_formats = [
                fmt
                for fmt, success in results.items()
                if not success and fmt != "original_tiff_mets"
            ]

            # Verificar si se generó el METS del TIFF original
            original_tiff_success = results.get("original_tiff_mets", False)
            if original_tiff_success:
                output_manager.success(
                    f"Archivo METS del TIFF original generado para {subfolder_name}"
                )
            else:
                output_manager.error(
                    f"Error generando archivo METS del TIFF original para {subfolder_name}"
                )

            if successful_formats:
                output_manager.success(
                    f"Archivos MET generados para {subfolder_name}: {', '.join(successful_formats)}"
                )
            if failed_formats:
                output_manager.error(
                    f"Errores generando MET para {subfolder_name}: {', '.join(failed_formats)}"
                )

            return len(failed_formats) == 0

        except Exception as e:
            output_manager.error(f"Error en postconversor MET: {str(e)}")
            return False

    def _prepare_conversion_results(
        self, conversion_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
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

            # Los datos ya están en file_info, no necesitamos buscar en conversions
            if file_info.get("success", False):
                output_path = Path(file_info["output_file"])
                try:
                    size = output_path.stat().st_size if output_path.exists() else 0
                except (OSError, FileNotFoundError):
                    size = 0
                output_files.append(
                    {
                        "format": file_info["format"],
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
        Crea archivos MET específicos para cada formato y un archivo METS del TIFF original

        Args:
            conversion_results: Resultados de conversión preparados
            output_dir: Directorio de salida

        Returns:
            Diccionario con el resultado por formato y el METS del TIFF original
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
                    output_manager.info(
                        f"Debug - Formato: {format_type}, Tamaño: {size_value} (tipo: {type(size_value)})"
                    )

                    files_by_format[format_type].append(
                        {
                            "input_file": result["input_file"],
                            "output_file": {
                                "path": output_file["path"],
                                "size": size_value,
                            },
                        }
                    )

        # Generar archivo METS del TIFF original
        try:
            success = self._create_original_tiff_mets_file(
                conversion_results, output_dir
            )
            results["original_tiff_mets"] = success
            if success:
                output_manager.success(
                    "Archivo METS del TIFF original generado exitosamente"
                )
            else:
                output_manager.warning("Error generando archivo METS del TIFF original")
        except Exception as e:
            output_manager.error(
                f"Error generando archivo METS del TIFF original: {str(e)}"
            )
            results["original_tiff_mets"] = False

        # Generar archivo MET para cada formato
        for format_type, files in files_by_format.items():
            try:
                success = self._create_single_format_met_file(
                    format_type, files, output_dir
                )
                results[format_type] = success
            except Exception as e:
                output_manager.error(
                    f"Error generando archivo MET para {format_type}: {str(e)}"
                )
                results[format_type] = False

        return results

    def _create_format_specific_met_for_subfolder(
        self,
        conversion_results: List[Dict[str, Any]],
        output_dir: Path,
        subfolder_name: str,
    ) -> Dict[str, bool]:
        """
        Crea archivos MET por formato para una subcarpeta específica

        Args:
            conversion_results: Lista de resultados de conversión
            output_dir: Directorio de salida raíz
            subfolder_name: Nombre de la subcarpeta

        Returns:
            Diccionario con el resultado de cada formato
        """
        results = {}

        try:
            # Crear directorio de la subcarpeta en la salida
            subfolder_output_dir = output_dir / subfolder_name
            subfolder_output_dir.mkdir(parents=True, exist_ok=True)

            # Generar archivos MET por formato
            for format_name in ["JPGHIGH", "JPGLOW", "PDF"]:
                if self._has_files_for_format(conversion_results, format_name):
                    success = self._create_format_met_file(
                        conversion_results,
                        subfolder_output_dir,
                        format_name,
                        subfolder_name,
                    )
                    results[format_name] = success
                else:
                    results[format_name] = False

            # Generar archivo METS del TIFF original para esta subcarpeta
            original_tiff_success = self._create_original_tiff_mets_file(
                conversion_results, subfolder_output_dir
            )
            results["original_tiff_mets"] = original_tiff_success

        except Exception as e:
            output_manager.error(
                f"Error generando archivos MET para subcarpeta {subfolder_name}: {str(e)}"
            )
            # Marcar todos como fallidos
            for format_name in ["JPGHIGH", "JPGLOW", "PDF"]:
                results[format_name] = False
            results["original_tiff_mets"] = False

        return results

    def _has_files_for_format(
        self, conversion_results: List[Dict[str, Any]], format_name: str
    ) -> bool:
        """Verifica si hay archivos para un formato específico"""
        for result in conversion_results:
            if result.get("success", False):
                for output_file in result.get("output_files", []):
                    if output_file.get("format") == format_name:
                        return True
        return False

    def _create_format_met_file(
        self,
        conversion_results: List[Dict[str, Any]],
        subfolder_output_dir: Path,
        format_name: str,
        subfolder_name: str,
    ) -> bool:
        """
        Crea un archivo MET para un formato específico en una subcarpeta

        Args:
            conversion_results: Lista de resultados de conversión
            subfolder_output_dir: Directorio de salida de la subcarpeta
            format_name: Nombre del formato
            subfolder_name: Nombre de la subcarpeta

        Returns:
            True si se creó exitosamente
        """
        try:
            # Filtrar resultados para este formato
            format_results = []
            for result in conversion_results:
                if result.get("success", False):
                    for output_file in result.get("output_files", []):
                        if output_file.get("format") == format_name:
                            format_results.append(
                                {
                                    "input_file": result["input_file"],
                                    "output_file": output_file,
                                }
                            )

            if not format_results:
                return False

            # Crear directorio METS si no existe
            mets_dir = subfolder_output_dir / "METS"
            mets_dir.mkdir(exist_ok=True)

            # Crear archivo MET para este formato en la carpeta METS
            met_file_path = mets_dir / f"{format_name}.xml"

            # Generar contenido XML
            xml_content = self._generate_format_met_xml(
                format_results, format_name, subfolder_name
            )

            # Escribir archivo
            with open(met_file_path, "w", encoding="utf-8") as f:
                f.write(xml_content)

            output_manager.success(
                f"Archivo MET generado: {subfolder_name}/METS/{format_name}.xml"
            )
            return True

        except Exception as e:
            output_manager.error(
                f"Error generando archivo MET para {format_name} en {subfolder_name}: {str(e)}"
            )
            return False

    def _generate_format_met_xml(
        self,
        format_results: List[Dict[str, Any]],
        format_name: str,
        subfolder_name: str,
    ) -> str:
        """
        Genera el contenido XML para un archivo MET de formato específico

        Args:
            format_results: Resultados del formato específico
            format_name: Nombre del formato
            subfolder_name: Nombre de la subcarpeta

        Returns:
            Contenido XML generado
        """
        # Implementar generación de XML específico para el formato
        # Este es un placeholder - se debe implementar la lógica completa
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        xml_content = f"""<?xml version='1.0' encoding='utf-8'?>
<mets xmlns="http://www.loc.gov/METS/" xmlns:xlink="http://www.w3.org/1999/xlink">
  <objid>MET_{format_name}_{subfolder_name}_{timestamp}</objid>
  <agent ROLE="CREATOR" TYPE="ORGANIZATION">
    <name>{self.organization}</name>
  </agent>
  <metsHdr CREATEDATE="{datetime.now().isoformat()}" LASTMODDATE="{datetime.now().isoformat()}">
    <agent ROLE="CREATOR" TYPE="OTHER" OTHERTYPE="SOFTWARE">
      <name>Conversor TIFF v2.0</name>
    </agent>
  </metsHdr>
  <fileSec>
    <fileGrp USE="PRESERVATION">
      <!-- Archivos del formato {format_name} para subcarpeta {subfolder_name} -->
    </fileGrp>
  </fileSec>
</mets>"""

        return xml_content

    def _generate_original_tiff_mets_xml(
        self, conversion_results: List[Dict[str, Any]], subfolder_name: str
    ) -> str:
        """
        Genera el contenido XML para el archivo METS del TIFF original

        Args:
            conversion_results: Lista de resultados de conversión
            subfolder_name: Nombre de la subcarpeta

        Returns:
            Contenido XML generado
        """
        # Implementar generación de XML del METS del TIFF original
        # Este es un placeholder - se debe implementar la lógica completa
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        xml_content = f"""<?xml version='1.0' encoding='utf-8'?>
<mets xmlns="http://www.loc.gov/METS/" xmlns:xlink="http://www.w3.org/1999/xlink">
  <objid>METS_{subfolder_name}_TIFF_{timestamp}</objid>
  <agent ROLE="CREATOR" TYPE="ORGANIZATION">
    <name>{self.organization}</name>
  </agent>
  <metsHdr CREATEDATE="{datetime.now().isoformat()}" LASTMODDATE="{datetime.now().isoformat()}">
    <agent ROLE="CREATOR" TYPE="OTHER" OTHERTYPE="SOFTWARE">
      <name>Conversor TIFF v2.0</name>
    </agent>
  </metsHdr>
  <fileSec>
    <fileGrp USE="PRESERVATION">
      <!-- Archivos TIFF originales de la subcarpeta {subfolder_name} -->
    </fileGrp>
  </fileSec>
</mets>"""

        return xml_content

    def _create_single_format_met_file(
        self, format_type: str, files: List[Dict[str, Any]], output_dir: Path
    ) -> bool:
        """
        Crea un archivo XML MET único para un formato específico (diferente del archivo METS del TIFF original)

        Args:
            format_type: Tipo de formato (jpg_400, pdf_easyocr, etc.)
            files: Lista de archivos del formato
            output_dir: Directorio de salida

        Returns:
            True si se creó correctamente
        """
        try:
            output_manager.info(
                f"Debug - Iniciando creación de archivo MET para formato: {format_type}"
            )
            output_manager.info(f"Debug - Número de archivos: {len(files)}")
            output_manager.info(f"Debug - Directorio de salida: {output_dir}")

            # Crear elemento raíz MET
            root = ET.Element("mets")
            root.set("xmlns", "http://www.loc.gov/METS/")
            root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
            root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            root.set(
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
                "http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd",
            )

            # Agregar información del objeto
            objid = ET.SubElement(root, "objid")
            objid.text = (
                f"MET_{format_type.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

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

            # Agregar cada archivo del formato
            for file_info in files:
                input_path = Path(file_info["input_file"])
                output_file = file_info["output_file"]

                # Crear grupo de archivos para este TIFF original
                file_grp = ET.SubElement(file_sec, "fileGrp")
                file_grp.set("USE", "PRESERVATION")

                # Información del archivo TIFF original
                file_elem_orig = ET.SubElement(file_grp, "file")
                file_elem_orig.set("ID", f"FILE_{input_path.stem}_ORIGINAL")
                file_elem_orig.set("MIMETYPE", "image/tiff")
                file_elem_orig.set("SIZE", str(input_path.stat().st_size))
                timestamp = input_path.stat().st_ctime
                created_time = datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                file_elem_orig.set("CREATED", created_time)
                file_elem_orig.set("CHECKSUM", self._calculate_checksum(input_path))
                file_elem_orig.set("CHECKSUMTYPE", "MD5")

                # Ubicación del archivo TIFF original
                flocat_orig = ET.SubElement(file_elem_orig, "FLocat")
                href_value = str(input_path.absolute())
                flocat_orig.set("{http://www.w3.org/1999/xlink}href", href_value)

                # Agregar metadatos del archivo TIFF original
                if self.include_file_metadata:
                    self._add_file_metadata(file_elem_orig, input_path)

                # Agregar metadatos de imagen del TIFF original
                if self.include_image_metadata:
                    self._add_image_metadata(file_elem_orig, input_path)

                # Información del archivo convertido
                file_elem_conv = ET.SubElement(file_grp, "file")
                file_elem_conv.set(
                    "ID", f"FILE_{input_path.stem}_{format_type.upper()}"
                )
                file_elem_conv.set("MIMETYPE", self._get_mime_type(format_type))
                try:
                    size_value = int(output_file["size"])
                    file_elem_conv.set("SIZE", str(size_value))
                except (ValueError, TypeError):
                    file_elem_conv.set("SIZE", "0")
                file_elem_conv.set("CREATED", creation_date)
                file_elem_conv.set(
                    "CHECKSUM", self._calculate_checksum(output_file["path"])
                )
                file_elem_conv.set("CHECKSUMTYPE", "MD5")

                # Ubicación del archivo convertido
                flocat_conv = ET.SubElement(file_elem_conv, "FLocat")
                href_value_conv = str(output_file["path"].absolute())
                flocat_conv.set("{http://www.w3.org/1999/xlink}href", href_value_conv)

                # Agregar metadatos del archivo convertido
                if self.include_file_metadata:
                    self._add_file_metadata(file_elem_conv, output_file["path"])

                # Agregar metadatos de imagen si es aplicable
                if self.include_image_metadata and format_type in [
                    "JPGHIGH",
                    "JPGLOW",
                ]:
                    output_manager.info(
                        f"Debug - Agregando metadatos de imagen para: {input_path}"
                    )
                    try:
                        self._add_image_metadata(file_elem_conv, input_path)
                        output_manager.info(
                            f"Debug - Metadatos de imagen agregados exitosamente"
                        )
                    except Exception as e:
                        output_manager.error(f"Error en _add_image_metadata: {str(e)}")
                        output_manager.error(f"Tipo de error: {type(e)}")

            # Agregar sección de metadatos administrativos con tab premis
            output_manager.info(f"Debug - Creando sección PREMIS")
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
            output_manager.info(f"Debug - Creando objetos PREMIS")
            objects_elem = ET.SubElement(premis_root, "objects")
            for i, file_info in enumerate(files):
                output_file = file_info["output_file"]
                try:
                    size_value = int(output_file["size"])
                    output_manager.info(
                        f"Debug - Procesando objeto PREMIS {i+1}/{len(files)}"
                    )
                    output_manager.info(f"Debug - Tamaño PREMIS: {size_value}")
                except (ValueError, TypeError) as e:
                    output_manager.warning(f"Error en tamaño PREMIS: {e}")
                    size_value = 0

                # Crear objeto PREMIS
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
                size_elem.text = str(size_value)

                # Formato
                format_elem = ET.SubElement(object_characteristics, "format")
                format_designation = ET.SubElement(format_elem, "formatDesignation")
                format_name = ET.SubElement(format_designation, "formatName")
                format_name.text = format_type

                # Creación
                creation_elem = ET.SubElement(object_characteristics, "creation")
                creation_date_elem = ET.SubElement(creation_elem, "dateCreated")
                creation_date_elem.text = creation_date
                output_manager.info(f"Debug - Objeto PREMIS {i+1} completado")

            output_manager.info(f"Debug - Sección PREMIS completada")

            # Crear y guardar el archivo XML en la carpeta METS
            filename = f"{format_type}.xml"
            output_manager.info(
                f"Debug - filename: {filename} (tipo: {type(filename)})"
            )
            output_manager.info(
                f"Debug - output_dir: {output_dir} (tipo: {type(output_dir)})"
            )

            # Crear la carpeta METS si no existe
            mets_subdir = output_dir / "METS"
            mets_subdir.mkdir(exist_ok=True)

            output_path = mets_subdir / filename
            output_manager.info(
                f"Debug - output_path creado: {output_path} (tipo: {type(output_path)})"
            )
            output_manager.info(f"Debug - Creando archivo XML: {output_path}")

            tree = ET.ElementTree(root)
            output_manager.info(f"Debug - Árbol XML creado")
            self._indent_xml_tree(tree)
            output_manager.info(f"Debug - XML indentado")
            tree.write(output_path, encoding="utf-8", xml_declaration=True)
            output_manager.info(f"Debug - Archivo XML escrito exitosamente")

            return True

        except Exception as e:
            output_manager.error(
                f"Error creando archivo MET único para {format_type}: {str(e)}"
            )
            return False

    def _create_original_tiff_mets_file(
        self, conversion_results: List[Dict[str, Any]], output_dir: Path
    ) -> bool:
        """
        Crea un archivo METS único para el TIFF original

        Args:
            conversion_results: Resultados de conversión preparados
            output_dir: Directorio de salida

        Returns:
            True si se creó correctamente
        """
        try:
            output_manager.info(
                f"Debug - Iniciando creación de archivo METS del TIFF original"
            )
            output_manager.info(
                f"Debug - Número de archivos de entrada: {len(conversion_results)}"
            )

            # Crear elemento raíz METS
            root = ET.Element("mets")
            root.set("xmlns", "http://www.loc.gov/METS/")
            root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
            root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            root.set(
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
                "http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd",
            )

            # Agregar información del objeto
            objid = ET.SubElement(root, "objid")
            objid.text = f"MET_ORIGINAL_TIFF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

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

            # Agregar cada archivo de entrada (TIFF original)
            for file_info in conversion_results:
                input_path = Path(file_info["input_file"])

                # Crear grupo de archivos para este TIFF original
                file_grp = ET.SubElement(file_sec, "fileGrp")
                file_grp.set("USE", "PRESERVATION")

                # Información del archivo TIFF original
                file_elem_orig = ET.SubElement(file_grp, "file")
                file_elem_orig.set("ID", f"FILE_{input_path.stem}_ORIGINAL")
                file_elem_orig.set("MIMETYPE", "image/tiff")
                file_elem_orig.set("SIZE", str(input_path.stat().st_size))
                timestamp = input_path.stat().st_ctime
                created_time = datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                file_elem_orig.set("CREATED", created_time)
                file_elem_orig.set("CHECKSUM", self._calculate_checksum(input_path))
                file_elem_orig.set("CHECKSUMTYPE", "MD5")

                # Ubicación del archivo TIFF original
                flocat_orig = ET.SubElement(file_elem_orig, "FLocat")
                href_value = str(input_path.absolute())
                flocat_orig.set("{http://www.w3.org/1999/xlink}href", href_value)

                # Agregar metadatos del archivo TIFF original
                if self.include_file_metadata:
                    self._add_file_metadata(file_elem_orig, input_path)

                # Agregar metadatos de imagen del TIFF original
                if self.include_image_metadata:
                    self._add_image_metadata(file_elem_orig, input_path)

            # Agregar sección de metadatos administrativos con tab premis
            output_manager.info(f"Debug - Creando sección PREMIS para METS original")
            amd_sec = ET.SubElement(root, "amdSec")
            premis_md = ET.SubElement(amd_sec, "premisMD")
            premis_md.set("ID", "PREMIS_ORIGINAL_TIFF")

            md_wrap = ET.SubElement(premis_md, "mdWrap")
            md_wrap.set("MDTYPE", "PREMIS")
            md_wrap.set("OTHERMDTYPE", "PREMIS")

            xml_data = ET.SubElement(md_wrap, "xmlData")

            # Crear estructura PREMIS
            premis_root = ET.SubElement(xml_data, "premis")
            premis_root.set("xmlns", "http://www.loc.gov/premis/v3")
            premis_root.set("version", "3.0")

            # Agregar objetos (archivos)
            output_manager.info(f"Debug - Creando objetos PREMIS para METS original")
            objects_elem = ET.SubElement(premis_root, "objects")
            for i, file_info in enumerate(conversion_results):
                input_path = Path(file_info["input_file"])
                try:
                    size_value = int(input_path.stat().st_size)
                    output_manager.info(
                        f"Debug - Procesando objeto PREMIS original {i+1}/{len(conversion_results)}"
                    )
                    output_manager.info(f"Debug - Tamaño PREMIS original: {size_value}")
                except (ValueError, TypeError) as e:
                    output_manager.warning(f"Error en tamaño PREMIS original: {e}")
                    size_value = 0

                # Crear objeto PREMIS
                object_elem = ET.SubElement(objects_elem, "object")
                # Simplificar para evitar problemas de namespace
                # object_elem.set("{http://www.w3.org/2001/XMLSchema-instance}type", "representation")

                # Identificador del objeto
                object_id = ET.SubElement(object_elem, "objectIdentifier")
                object_id_value = ET.SubElement(object_id, "objectIdentifierValue")
                object_id_value.text = f"{input_path.stem}_ORIGINAL"
                object_id_type = ET.SubElement(object_id, "objectIdentifierType")
                object_id_type.text = "LOCAL"

                # Características del objeto
                object_characteristics = ET.SubElement(
                    object_elem, "objectCharacteristics"
                )

                # Tamaño
                size_elem = ET.SubElement(object_characteristics, "size")
                size_elem.text = str(size_value)

                # Formato
                format_elem = ET.SubElement(object_characteristics, "format")
                format_designation = ET.SubElement(format_elem, "formatDesignation")
                format_name = ET.SubElement(format_designation, "formatName")
                format_name.text = "TIFF"

                # Creación
                creation_elem = ET.SubElement(object_characteristics, "creation")
                creation_date_elem = ET.SubElement(creation_elem, "dateCreated")
                creation_date_elem.text = creation_date
                output_manager.info(f"Debug - Objeto PREMIS original {i+1} completado")

            output_manager.info(f"Debug - Sección PREMIS para METS original completada")

            # Crear y guardar el archivo XML en la carpeta del formato correspondiente
            filename = "TIFF.xml"
            output_manager.info(
                f"Debug - filename: {filename} (tipo: {type(filename)})"
            )
            output_manager.info(
                f"Debug - output_dir: {output_dir} (tipo: {type(output_dir)})"
            )

            # Crear la carpeta del formato si no existe
            original_tiff_subdir = output_dir / "METS"
            original_tiff_subdir.mkdir(exist_ok=True)

            output_path = original_tiff_subdir / filename
            output_manager.info(
                f"Debug - output_path creado: {output_path} (tipo: {type(output_path)})"
            )
            output_manager.info(f"Debug - Creando archivo XML: {output_path}")

            tree = ET.ElementTree(root)
            output_manager.info(f"Debug - Árbol XML creado")
            self._indent_xml_tree(tree)
            output_manager.info(f"Debug - XML indentado")
            tree.write(output_path, encoding="utf-8", xml_declaration=True)
            output_manager.info(f"Debug - Archivo XML escrito exitosamente")

            return True
        except Exception as e:
            output_manager.error(
                f"Error generando archivo METS del TIFF original: {str(e)}"
            )
            return False

    def _add_file_metadata(self, file_elem: ET.Element, input_path: Path) -> None:
        """
        Agrega metadatos del archivo al elemento MET

        Args:
            file_elem: Elemento file del MET
            input_path: Ruta del archivo de entrada
        """
        try:
            output_manager.info(
                f"Debug - Agregando metadatos para archivo: {input_path}"
            )
            stat = input_path.stat()
            output_manager.info(
                f"Debug - stat.st_size: {stat.st_size} (tipo: {type(stat.st_size)})"
            )

            # Información del archivo
            file_info = ET.SubElement(file_elem, "fileInfo")
            file_info.set("name", input_path.name)
            file_info.set("extension", input_path.suffix)

            # Asegurar que el tamaño sea un entero
            try:
                size_bytes = int(stat.st_size)
                output_manager.info(
                    f"Debug - size_bytes convertido: {size_bytes} (tipo: {type(size_bytes)})"
                )
                file_info.set("size_bytes", str(size_bytes))
            except (TypeError, ValueError) as e:
                output_manager.warning(
                    f"Error convirtiendo tamaño del archivo {input_path}: {stat.st_size}, error: {e}"
                )
                file_info.set("size_bytes", "0")
                size_bytes = 0

            # Calcular tamaño en MB de forma segura
            try:
                output_manager.info(
                    f"Debug - Antes de división: size_bytes={size_bytes}, tipo={type(size_bytes)}"
                )
                if size_bytes > 0:
                    size_mb = f"{size_bytes / (1024 * 1024):.2f}"
                    output_manager.info(f"Debug - División exitosa: {size_mb}")
                else:
                    size_mb = "0.00"
                    output_manager.info(f"Debug - Tamaño 0, usando valor por defecto")
                file_info.set("size_mb", size_mb)
            except (TypeError, ValueError) as e:
                output_manager.warning(
                    f"Error calculando tamaño en MB para {input_path}: {e}"
                )
                file_info.set("size_mb", "0.00")

            # Información de fechas
            try:
                created_time = datetime.fromtimestamp(stat.st_ctime).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                file_info.set("created", created_time)
            except (TypeError, ValueError):
                file_info.set("created", "1970-01-01T00:00:00")

            try:
                modified_time = datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                file_info.set("modified", modified_time)
            except (TypeError, ValueError):
                file_info.set("modified", "1970-01-01T00:00:00")

            try:
                accessed_time = datetime.fromtimestamp(stat.st_atime).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                file_info.set("accessed", accessed_time)
            except (TypeError, ValueError):
                file_info.set("accessed", "1970-01-01T00:00:00")

            # Información de permisos
            try:
                permissions = oct(stat.st_mode)[-3:]
                file_info.set("permissions", permissions)
            except (TypeError, ValueError):
                file_info.set("permissions", "000")

        except Exception as e:
            output_manager.error(
                f"Error obteniendo metadatos del archivo {input_path}: {str(e)}"
            )
            output_manager.error(f"Tipo de error: {type(e)}")
            # Crear elementos con valores por defecto
            file_info = ET.SubElement(file_elem, "fileInfo")
            file_info.set("name", input_path.name if input_path else "unknown")
            file_info.set("extension", input_path.suffix if input_path else "")
            file_info.set("size_bytes", "0")
            file_info.set("size_mb", "0.00")
            file_info.set("created", "1970-01-01T00:00:00")
            file_info.set("modified", "1970-01-01T00:00:00")
            file_info.set("accessed", "1970-01-01T00:00:00")
            file_info.set("permissions", "000")

    def _add_image_metadata(self, file_elem: ET.Element, input_path: Path) -> None:
        """
        Agrega metadatos de imagen al elemento MET

        Args:
            file_elem: Elemento file del MET
            input_path: Ruta del archivo de entrada
        """
        try:
            output_manager.info(
                f"Debug - Iniciando _add_image_metadata para: {input_path}"
            )
            from PIL import Image

            with Image.open(input_path) as img:
                output_manager.info(
                    f"Debug - Imagen abierta: {img.width}x{img.height}, modo: {img.mode}"
                )

                # Información de imagen
                img_info = ET.SubElement(file_elem, "imageInfo")
                img_info.set("width", str(img.width))
                img_info.set("height", str(img.height))
                img_info.set("mode", img.mode)
                img_info.set("format", img.format or "TIFF")

                # Información de DPI si está disponible
                if hasattr(img, "info") and "dpi" in img.info:
                    dpi_x, dpi_y = img.info["dpi"]
                    output_manager.info(f"Debug - DPI encontrado: {dpi_x}x{dpi_y}")
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
                                    8: "Rotate 270 CW",
                                }
                                orientation_value = orientation_values.get(
                                    orientation, "Unknown"
                                )
                                img_info.set("orientation", orientation_value)
                                output_manager.info(
                                    f"Debug - Orientación: {orientation_value}"
                                )
                    except Exception as easyocr_error:
                        output_manager.error(
                            f"Error obteniendo metadatos de imagen: {str(easyocr_error)}"
                        )
                        pass

            output_manager.info(f"Debug - _add_image_metadata completado exitosamente")

        except Exception as e:
            output_manager.error(f"Error obteniendo metadatos de imagen: {str(e)}")
            output_manager.error(f"Tipo de error: {type(e)}")

    def _indent_xml_tree(self, tree: ET.ElementTree, space: str = "  ") -> None:
        """
        Indenta un árbol XML de forma compatible con Python 3.8

        Args:
            tree: Árbol XML a indentar
            space: Espacio de indentación
        """

        def _indent(elem, level=0):
            i = "\n" + level * space
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + space
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for subelem in elem:
                    _indent(subelem, level + 1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i

        _indent(tree.getroot())

    def _get_mime_type(self, format_type: str) -> str:
        """
        Retorna el MIME type correspondiente al formato

        Args:
            format_type: Tipo de formato

        Returns:
            MIME type correspondiente
        """
        mime_types = {
            "JPGHIGH": "image/jpeg",
            "JPGLOW": "image/jpeg",
            "PDF": "application/pdf",
            "METS": "application/xml",
        }
        return mime_types.get(format_type, "application/octet-stream")

    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calcula el checksum MD5 de un archivo

        Args:
            file_path: Ruta del archivo

        Returns:
            Checksum MD5 en formato hexadecimal
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return "00000000000000000000000000000000"
