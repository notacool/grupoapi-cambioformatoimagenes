"""
Conversor de TIFF a archivo XML MET (Metadata Encoding and Transmission Standard)
"""

import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from PIL import Image

from .base import BaseConverter


class METMetadataConverter(BaseConverter):
    """Conversor de TIFF a archivo XML MET con metadatos detallados"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el conversor MET

        Args:
            config: Configuración del conversor
        """
        super().__init__(config)
        self.include_image_metadata = config.get('include_image_metadata', True)
        self.include_file_metadata = config.get('include_file_metadata', True)
        self.include_processing_info = config.get('include_processing_info', True)
        self.metadata_standard = config.get('metadata_standard', 'MET')
        self.organization = config.get('organization', 'Conversor TIFF')
        self.creator = config.get('creator', 'Sistema Automatizado')

    def convert(self, input_path: Path, output_path: Path) -> bool:
        """
        Convierte un archivo TIFF a archivo XML MET con metadatos

        Args:
            input_path: Ruta del archivo TIFF de entrada
            output_path: Ruta del archivo XML MET de salida

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
                print(f"Error: No se pudo crear el directorio de salida: {output_path.parent}")
                return False

            # Generar metadatos MET
            success = self._create_met_xml(input_path, output_path)
            if success:
                print(f"✅ Metadatos MET generados: {input_path.name} -> {output_path.name}")
            return success

        except Exception as e:
            print(f"❌ Error generando metadatos MET: {str(e)}")
            return False

    def _create_met_xml(self, input_path: Path, output_path: Path) -> bool:
        """
        Crea un archivo XML MET con metadatos del archivo TIFF

        Args:
            input_path: Archivo TIFF de entrada
            output_path: Archivo XML MET de salida

        Returns:
            True si se creó correctamente
        """
        try:
            # Crear elemento raíz MET
            root = ET.Element('met')
            root.set('xmlns', 'http://www.loc.gov/METS/')
            root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
            root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            root.set('xsi:schemaLocation',
                     'http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd')

            # Agregar información del objeto
            objid = ET.SubElement(root, 'objid')
            objid.text = str(input_path.stem)

            # Agregar información del agente
            agent = ET.SubElement(root, 'agent')
            agent.set('ROLE', 'CREATOR')
            agent.set('TYPE', 'ORGANIZATION')
            name = ET.SubElement(agent, 'name')
            name.text = self.organization

            # Agregar información de creación
            creation_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            mets_hdr = ET.SubElement(root, 'metsHdr')
            mets_hdr.set('CREATEDATE', creation_date)
            mets_hdr.set('LASTMODDATE', creation_date)
            agent_hdr = ET.SubElement(mets_hdr, 'agent')
            agent_hdr.set('ROLE', 'CREATOR')
            agent_hdr.set('TYPE', 'OTHER')
            agent_hdr.set('OTHERTYPE', 'SOFTWARE')
            name_hdr = ET.SubElement(agent_hdr, 'name')
            name_hdr.text = self.creator

            # Agregar información del archivo
            file_sec = ET.SubElement(root, 'fileSec')
            file_grp = ET.SubElement(file_sec, 'fileGrp')
            file_grp.set('USE', 'PRESERVATION')

            # Información del archivo original
            file_elem = ET.SubElement(file_grp, 'file')
            file_elem.set('ID', f"FILE_{input_path.stem}")
            file_elem.set('MIMETYPE', 'image/tiff')
            file_elem.set('SIZE', str(input_path.stat().st_size))
            timestamp = input_path.stat().st_ctime
            created_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
            file_elem.set('CREATED', created_time)
            file_elem.set('CHECKSUM', self._calculate_checksum(input_path))
            file_elem.set('CHECKSUMTYPE', 'MD5')

            # Ubicación del archivo
            flocat = ET.SubElement(file_elem, 'FLocat')
            href_value = str(input_path.absolute())
            flocat.set('xlink:href', href_value)

            # Agregar metadatos técnicos si están habilitados
            if self.include_image_metadata:
                self._add_image_metadata(file_elem, input_path)

            # Agregar metadatos del archivo si están habilitados
            if self.include_file_metadata:
                self._add_file_metadata(file_elem, input_path)

            # Agregar información de procesamiento si está habilitada
            if self.include_processing_info:
                self._add_processing_info(file_elem)

            # Agregar sección de metadatos administrativos
            amd_sec = ET.SubElement(root, 'amdSec')
            tech_md = ET.SubElement(amd_sec, 'techMD')
            tech_md.set('ID', f"TECHMD_{input_path.stem}")
            md_wrap = ET.SubElement(tech_md, 'mdWrap')
            md_wrap.set('MDTYPE', 'OTHER')
            md_wrap.set('OTHERMDTYPE', 'TECHNICAL')
            xml_data = ET.SubElement(md_wrap, 'xmlData')

            # Agregar metadatos técnicos detallados
            tech_info = ET.SubElement(xml_data, 'technicalInfo')
            tech_info.set('format', 'TIFF')
            tech_info.set('conversionDate', creation_date)
            tech_info.set('converter', self.creator)

            # Crear y guardar el archivo XML
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(output_path, encoding='utf-8', xml_declaration=True)

            return True

        except Exception as e:
            print(f"Error creando archivo MET: {str(e)}")
            return False

    def _add_image_metadata(self, file_elem: ET.Element, input_path: Path) -> None:
        """
        Agrega metadatos de imagen al archivo MET

        Args:
            file_elem: Elemento file del MET
            input_path: Archivo TIFF de entrada
        """
        try:
            with Image.open(input_path) as img:
                # Información básica de la imagen
                img_info = ET.SubElement(file_elem, 'imageInfo')
                img_info.set('width', str(img.width))
                img_info.set('height', str(img.height))
                img_info.set('mode', img.mode)
                img_info.set('format', img.format)

                # Información de DPI si está disponible
                if 'dpi' in img.info:
                    dpi_info = img.info['dpi']
                    if dpi_info:
                        img_info.set('dpi_x', str(dpi_info[0]))
                        img_info.set('dpi_y', str(dpi_info[1]))

                # Información de compresión si está disponible
                if 'compression' in img.info:
                    img_info.set('compression', str(img.info['compression']))

                # Información de orientación si está disponible
                if hasattr(img, '_getexif'):
                    try:
                        exif = img._getexif()
                        if exif and 274 in exif:  # Orientation tag
                            orientation = exif[274]
                            orientation_names = {
                                1: 'Normal',
                                2: 'Mirror horizontal',
                                3: 'Rotate 180',
                                4: 'Mirror vertical',
                                5: 'Mirror horizontal and rotate 270 CW',
                                6: 'Rotate 270 CW',
                                7: 'Mirror horizontal and rotate 90 CW',
                                8: 'Rotate 90 CW'
                            }
                            orientation_value = orientation_names.get(orientation, str(orientation))
                            img_info.set('orientation', orientation_value)
                    except Exception:
                        pass

        except Exception as e:
            print(f"Error obteniendo metadatos de imagen: {str(e)}")

    def _add_file_metadata(self, file_elem: ET.Element, input_path: Path) -> None:
        """
        Agrega metadatos del archivo al archivo MET

        Args:
            file_elem: Elemento file del MET
            input_path: Archivo TIFF de entrada
        """
        try:
            stat = input_path.stat()

            # Información del archivo
            file_info = ET.SubElement(file_elem, 'fileInfo')
            file_info.set('name', input_path.name)
            file_info.set('extension', input_path.suffix)
            file_info.set('size_bytes', str(stat.st_size))
            size_mb = f"{stat.st_size / (1024 * 1024):.2f}"
            file_info.set('size_mb', size_mb)
            created_time = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%dT%H:%M:%S')
            file_info.set('created', created_time)
            modified_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%dT%H:%M:%S')
            file_info.set('modified', modified_time)
            accessed_time = datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%dT%H:%M:%S')
            file_info.set('accessed', accessed_time)

            # Información de permisos
            permissions = oct(stat.st_mode)[-3:]
            file_info.set('permissions', permissions)

        except Exception as e:
            print(f"Error obteniendo metadatos del archivo: {str(e)}")

    def _add_processing_info(self, file_elem: ET.Element) -> None:
        """
        Agrega información de procesamiento al archivo MET

        Args:
            file_elem: Elemento file del MET
        """
        try:
            processing_info = ET.SubElement(file_elem, 'processingInfo')
            processing_info.set('converter', self.__class__.__name__)
            processing_info.set('conversion_date', datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
            processing_info.set('metadata_standard', self.metadata_standard)
            processing_info.set('version', '1.0')

            # Configuración del conversor
            config_info = ET.SubElement(processing_info, 'configuration')
            config_info.set('include_image_metadata', str(self.include_image_metadata))
            config_info.set('include_file_metadata', str(self.include_file_metadata))
            config_info.set('include_processing_info', str(self.include_processing_info))

        except Exception as e:
            print(f"Error agregando información de procesamiento: {str(e)}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calcula el checksum MD5 del archivo

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

    def get_file_extension(self) -> str:
        """Retorna la extensión del archivo XML MET"""
        return '.xml'

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
        format_subdir = output_dir / "met_metadata"
        format_subdir.mkdir(exist_ok=True)

        stem = input_path.stem
        extension = self.get_file_extension()
        filename = f"{stem}_MET{extension}"
        return format_subdir / filename

    def get_converter_info(self) -> Dict[str, Any]:
        """
        Retorna información específica del conversor MET

        Returns:
            Diccionario con información del conversor
        """
        base_info = super().get_converter_info()
        base_info.update({
            'metadata_standard': self.metadata_standard,
            'include_image_metadata': self.include_image_metadata,
            'include_file_metadata': self.include_file_metadata,
            'include_processing_info': self.include_processing_info,
            'organization': self.organization,
            'creator': self.creator,
            'format': 'XML MET'
        })
        return base_info
