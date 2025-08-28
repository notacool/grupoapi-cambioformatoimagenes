"""
Gestor de salida usando tqdm para mantener la barra de progreso siempre abajo
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict

from tqdm import tqdm


class OutputManager:
    """Gestor de salida que usa tqdm para mantener la barra de progreso siempre abajo"""

    def __init__(self):
        """Inicializa el gestor de salida"""
        self.main_pbar: tqdm = None
        self.info_pbar: tqdm = None
        self.log_file = None
        self.log_enabled = False
        self.verbose_mode = False

    def enable_file_logging(self, output_dir: str, subfolder_name: str = None):
        """
        Habilita el logging a archivo

        Args:
            output_dir: Directorio de salida
            subfolder_name: Nombre de la subcarpeta (opcional)
        """
        try:
            # Crear directorio de logs si no existe
            log_dir = Path(output_dir) / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            # Generar nombre del archivo de log
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if subfolder_name:
                log_filename = f"conversion_{subfolder_name}_{timestamp}.log"
            else:
                log_filename = f"conversion_{timestamp}.log"

            log_path = log_dir / log_filename
            self.log_file = open(log_path, "w", encoding="utf-8")
            self.log_enabled = True

            # Escribir encabezado del log
            self._write_to_log(f"=== LOG DE CONVERSIÓN TIFF ===")
            self._write_to_log(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            if subfolder_name:
                self._write_to_log(f"Subcarpeta: {subfolder_name}")
            self._write_to_log(f"Archivo de log: {log_path}")
            self._write_to_log("=" * 50)

        except Exception as e:
            print(f"❌ Error habilitando logging a archivo: {str(e)}")
            self.log_enabled = False

    def set_verbose_mode(self, verbose: bool):
        """Establece el modo verbose"""
        self.verbose_mode = verbose

    def _write_to_log(self, message: str):
        """Escribe un mensaje al archivo de log"""
        if self.log_enabled and self.log_file:
            try:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.log_file.write(f"[{timestamp}] {message}\n")
                self.log_file.flush()
            except Exception:
                pass

    def set_main_progress_bar(self, pbar: tqdm):
        """Establece la barra de progreso principal"""
        self.main_pbar = pbar

    def set_info_progress_bar(self, pbar: tqdm):
        """Establece la barra de progreso para información"""
        self.info_pbar = pbar

    def write(self, message: str, position: int = 0):
        """
        Escribe un mensaje en la posición especificada

        Args:
            message: Mensaje a escribir
            position: Posición donde escribir (0 = arriba, 1 = abajo)
        """
        # Siempre escribir al log
        self._write_to_log(message)

        # En modo no-verbose, solo mostrar mensajes importantes en pantalla
        if not self.verbose_mode and not self._is_important_message(message):
            return

        if position == 0 and self.main_pbar:
            # Escribir arriba de la barra principal
            self.main_pbar.write(message)
        elif position == 1 and self.info_pbar:
            # Escribir arriba de la barra de información
            self.info_pbar.write(message)
        else:
            # Fallback a print si no hay barras de progreso
            print(message)

    def _is_important_message(self, message: str) -> bool:
        """Determina si un mensaje es importante para mostrar en pantalla"""
        important_keywords = [
            "✅",
            "❌",
            "⚠️",
            "🚀",
            "📁",
            "📂",
            "📊",
            "🎯",
            "🔧",
            "⚙️",
            "Error:",
            "Error en",
            "Éxito",
            "Completado",
            "Falló",
            "Carpeta TIFF encontrada",
            "Estructura creada",
            "Archivos MET generados",
            "Conversión completada",
        ]

        return any(keyword in message for keyword in important_keywords)

    def info(self, message: str):
        """Escribe un mensaje informativo"""
        self.write(f"ℹ️  {message}", 0)

    def success(self, message: str):
        """Escribe un mensaje de éxito"""
        self.write(f"✅ {message}", 0)

    def error(self, message: str):
        """Escribe un mensaje de error"""
        self.write(f"❌ {message}", 0)

    def warning(self, message: str):
        """Escribe un mensaje de advertencia"""
        self.write(f"⚠️  {message}", 0)

    def section(self, title: str):
        """Escribe un título de sección"""
        self.write(f"\n{title}", 0)

    def separator(self, char: str = "=", length: int = 50):
        """Escribe un separador"""
        self.write(char * length, 0)

    def format_info(self, label: str, value: Any):
        """Formatea y escribe información etiquetada"""
        self.write(f"{label}: {value}", 0)

    def format_list(self, label: str, items: List[str]):
        """Formatea y escribe una lista"""
        if items:
            self.write(f"{label}: {', '.join(items)}", 0)
        else:
            self.write(f"{label}: (vacío)", 0)

    def log_subfolder_summary(self, subfolder_name: str, summary: Dict[str, Any]):
        """
        Escribe un resumen de subcarpeta al log

        Args:
            subfolder_name: Nombre de la subcarpeta
            summary: Resumen de conversiones
        """
        if not self.log_enabled:
            return

        self._write_to_log(f"\n=== RESUMEN SUBCARPETA: {subfolder_name} ===")
        self._write_to_log(f"Archivos totales: {summary.get('total_files', 0)}")
        self._write_to_log(f"Conversiones exitosas: {summary.get('successful', 0)}")
        self._write_to_log(f"Conversiones fallidas: {summary.get('failed', 0)}")
        self._write_to_log(
            f"Formatos procesados: {', '.join(summary.get('formats_processed', []))}"
        )
        self._write_to_log("=" * 50)

    def log_error_report(self, error_report: Dict[str, List[str]]):
        """
        Escribe un reporte de errores al log

        Args:
            error_report: Diccionario con errores por subcarpeta
        """
        if not self.log_enabled:
            return

        self._write_to_log(f"\n=== REPORTE DE ERRORES ===")
        for subfolder_name, errors in error_report.items():
            if errors:
                self._write_to_log(f"\nSubcarpeta: {subfolder_name}")
                for error in errors:
                    self._write_to_log(f"  ❌ {error}")
        self._write_to_log("=" * 50)

    def close(self):
        """Cierra todas las barras de progreso y el archivo de log"""
        if self.main_pbar:
            self.main_pbar.close()
        if self.info_pbar:
            self.info_pbar.close()
        if self.log_file:
            try:
                self._write_to_log(f"\n=== FIN DEL LOG ===")
                self._write_to_log(
                    f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                self.log_file.close()
            except Exception:
                pass


# Instancia global del gestor de salida
output_manager = OutputManager()
