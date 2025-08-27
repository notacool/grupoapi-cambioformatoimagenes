"""
Gestor de salida usando tqdm para mantener la barra de progreso siempre abajo
"""

from typing import Any, List

from tqdm import tqdm


class OutputManager:
    """Gestor de salida que usa tqdm para mantener la barra de progreso siempre abajo"""

    def __init__(self):
        """Inicializa el gestor de salida"""
        self.main_pbar: tqdm = None
        self.info_pbar: tqdm = None

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
        if position == 0 and self.main_pbar:
            # Escribir arriba de la barra principal
            self.main_pbar.write(message)
        elif position == 1 and self.info_pbar:
            # Escribir arriba de la barra de información
            self.info_pbar.write(message)
        else:
            # Fallback a print si no hay barras de progreso
            print(message)

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

    def close(self):
        """Cierra todas las barras de progreso"""
        if self.main_pbar:
            self.main_pbar.close()
        if self.info_pbar:
            self.info_pbar.close()


# Instancia global del gestor de salida
output_manager = OutputManager()
