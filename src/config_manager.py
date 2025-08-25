"""
Gestor de configuración para el conversor de archivos TIFF
"""

from pathlib import Path
from typing import Dict, Any, List
import yaml


class ConfigManager:
    """Gestor de configuración del conversor"""

    def __init__(self, config_path: str = None):
        """
        Inicializa el gestor de configuración

        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Obtiene la ruta por defecto del archivo de configuración"""
        # Buscar en el directorio actual o en el directorio del script
        current_dir = Path.cwd()
        script_dir = Path(__file__).parent.parent

        # Prioridad: directorio actual, luego directorio del script
        for search_dir in [current_dir, script_dir]:
            config_file = search_dir / "config.yaml"
            if config_file.exists():
                return str(config_file)

        # Si no existe, crear uno por defecto en el directorio actual
        return str(current_dir / "config.yaml")

    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo YAML"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    print(f"Configuración cargada desde: {self.config_path}")
            else:
                config = self._get_default_config()
                self._save_config(config)
                print(f"Archivo de configuración creado en: {self.config_path}")

            return self._validate_config(config)

        except Exception as e:
            print(f"Error cargando configuración: {str(e)}")
            print("Usando configuración por defecto")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna la configuración por defecto"""
        return {
            'formats': {
                'jpg_400': {
                    'enabled': True,
                    'quality': 95,
                    'optimize': True,
                    'progressive': False,
                    'dpi': 400
                },
                'jpg_200': {
                    'enabled': True,
                    'quality': 90,
                    'optimize': True,
                    'progressive': True,
                    'dpi': 200
                },
                'pdf_easyocr': {
                    'enabled': True,
                    'ocr_language': 'es',
                    'create_searchable_pdf': True,
                    'page_size': 'A4',
                    'fit_to_page': True,
                    'ocr_confidence': 0.5
                },
                'met_metadata': {
                    'enabled': True,
                    'include_image_metadata': True,
                    'include_file_metadata': True,
                    'include_processing_info': True,
                    'metadata_standard': 'MET',
                    'organization': 'Conversor TIFF',
                    'creator': 'Sistema Automatizado'
                }
            },
            'processing': {
                'max_workers': 4,
                'batch_size': 10,
                'overwrite_existing': False
            },
            'output': {
                'create_subdirectories': True,
                'naming_pattern': '{original_name}_{format}'
            }
        }

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y corrige la configuración si es necesario"""
        # Asegurar que todas las secciones existan
        if 'formats' not in config:
            config['formats'] = {}
        if 'processing' not in config:
            config['processing'] = {}
        if 'output' not in config:
            config['output'] = {}

        # Validar formatos
        default_formats = self._get_default_config()['formats']
        for format_name, format_config in default_formats.items():
            if format_name not in config['formats']:
                config['formats'][format_name] = format_config.copy()
            else:
                # Asegurar que todas las opciones del formato estén presentes
                for key, value in format_config.items():
                    if key not in config['formats'][format_name]:
                        config['formats'][format_name][key] = value

        # Validar procesamiento
        default_processing = self._get_default_config()['processing']
        for key, value in default_processing.items():
            if key not in config['processing']:
                config['processing'][key] = value

        # Validar salida
        default_output = self._get_default_config()['output']
        for key, value in default_output.items():
            if key not in config['output']:
                config['output'][key] = value

        return config

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Guarda la configuración en el archivo YAML"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error guardando configuración: {str(e)}")
            return False

    def get_format_config(self, format_name: str) -> Dict[str, Any]:
        """
        Obtiene la configuración para un formato específico

        Args:
            format_name: Nombre del formato (ej: 'jpg', 'pdf')

        Returns:
            Configuración del formato o configuración vacía si no existe
        """
        return self.config.get('formats', {}).get(format_name, {})

    def is_format_enabled(self, format_name: str) -> bool:
        """
        Verifica si un formato está habilitado

        Args:
            format_name: Nombre del formato

        Returns:
            True si el formato está habilitado
        """
        format_config = self.get_format_config(format_name)
        return format_config.get('enabled', False)

    def get_enabled_formats(self) -> List[str]:
        """
        Obtiene la lista de formatos habilitados

        Returns:
            Lista de nombres de formatos habilitados
        """
        enabled_formats = []
        for format_name, format_config in self.config.get('formats', {}).items():
            if format_config.get('enabled', False):
                enabled_formats.append(format_name)
        return enabled_formats

    def get_processing_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de procesamiento"""
        return self.config.get('processing', {})

    def get_output_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de salida"""
        return self.config.get('output', {})

    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Actualiza la configuración

        Args:
            new_config: Nueva configuración

        Returns:
            True si se actualizó correctamente
        """
        try:
            self.config.update(new_config)
            return self._save_config(self.config)
        except Exception as e:
            print(f"Error actualizando configuración: {str(e)}")
            return False

    def reload_config(self) -> bool:
        """
        Recarga la configuración desde el archivo

        Returns:
            True si se recargó correctamente
        """
        try:
            self.config = self._load_config()
            return True
        except Exception as e:
            print(f"Error recargando configuración: {str(e)}")
            return False
