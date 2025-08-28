#!/usr/bin/env python3
"""
Conversor de Archivos TIFF - Punto de entrada principal
"""

import sys
import traceback
from pathlib import Path

import click

from src.converter import TIFFConverter
from src.output_manager import output_manager


@click.command()
@click.option(
    "--input", "-i", "input_dir", help="Directorio de entrada con archivos TIFF"
)
@click.option(
    "--output", "-o", "output_dir", help="Directorio de salida para las conversiones"
)
@click.option(
    "--formats",
    "-f",
    help="Formatos específicos a convertir (ej: JPGHIGH,JPGLOW,PDF,METS)",
)
@click.option(
    "--config", "-c", "config_path", help="Archivo de configuración personalizado"
)
@click.option(
    "--workers",
    "-w",
    "max_workers",
    type=int,
    help="Número máximo de workers para procesamiento paralelo",
)
@click.option(
    "--list-formats", is_flag=True, help="Listar formatos disponibles y salir"
)
@click.option("--info", is_flag=True, help="Mostrar información del conversor y salir")
@click.option("--verbose", "-v", is_flag=True, help="Modo verbose con más información")
def main(
    input_dir,
    output_dir,
    formats,
    config_path,
    max_workers,
    list_formats,
    info,
    verbose,
):
    """
    Conversor de Archivos TIFF a múltiples formatos

    Convierte todos los archivos TIFF de un directorio a los formatos configurados.
    Los conversores se pueden configurar y agregar de manera modular.

    Ejemplos:
        python main.py --input "imagenes/" --output "convertidas/"
        python main.py --input "imagenes/" --output "convertidas/" --formats JPGHIGH,PDF
        python main.py --input "imagenes/" --output "convertidas/" --formats METS
        python main.py --input "imagenes/" --output "convertidas/" --config "mi_config.yaml"
    """

    try:
        # Inicializar conversor
        converter = TIFFConverter(config_path)

        # Mostrar información si se solicita
        if info:
            _show_converter_info(converter)
            return

        # Listar formatos si se solicita
        if list_formats:
            _list_available_formats(converter)
            return

        # Para conversión, se requieren directorios
        if not input_dir or not output_dir:
            output_manager.error("❌ Error: Se requieren --input y --output para la conversión")
            output_manager.info("   Use --help para ver todas las opciones disponibles")
            return

        # Validar directorios
        if not _validate_directories(input_dir, output_dir):
            return

        # Procesar formatos especificados
        format_list = None
        if formats:
            format_list = [f.strip().upper() for f in formats.split(",")]
            if verbose:
                output_manager.info(f"Formatos especificados: {format_list}")

        # Mostrar configuración si es verbose
        if verbose:
            _show_configuration(
                converter, input_dir, output_dir, format_list, max_workers
            )

        # Ejecutar conversión
        output_manager.info("\n🚀 Iniciando conversión de archivos TIFF...")
        result = converter.convert_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            formats=format_list,
            max_workers=max_workers,
        )

        # Mostrar resultado
        if result["success"]:
            output_manager.success("\n✅ Conversión completada exitosamente!")
            if verbose:
                _show_detailed_results(result)
        else:
            output_manager.error(f"\n❌ Error en la conversión: {result['error']}")
            sys.exit(1)

    except KeyboardInterrupt:
        output_manager.warning("\n\n⚠️  Conversión interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        output_manager.error(f"\n❌ Error inesperado: {str(e)}")
        if verbose:
            traceback.print_exc()
        sys.exit(1)


def _validate_directories(input_dir: str, output_dir: str) -> bool:
    """Valida que los directorios de entrada y salida sean válidos"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        output_manager.error(f"❌ El directorio de entrada no existe: {input_dir}")
        return False

    if not input_path.is_dir():
        output_manager.error(f"❌ La ruta de entrada no es un directorio: {input_dir}")
        return False

    # Crear directorio de salida si no existe
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        output_manager.error(f"❌ No se pudo crear el directorio de salida: {str(e)}")
        return False

    return True


def _show_converter_info(converter: TIFFConverter) -> None:
    """Muestra información del conversor"""
    output_manager.section("🔧 INFORMACIÓN DEL CONVERSOR TIFF")
    output_manager.separator()

    output_manager.format_info("📁 Formatos disponibles", converter.get_available_formats())
    output_manager.format_info("📋 Versión", "1.0.0")
    output_manager.format_info("🐍 Python", sys.version.split()[0])

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


def _list_available_formats(converter: TIFFConverter) -> None:
    """Lista los formatos disponibles"""
    output_manager.section("📋 FORMATOS DISPONIBLES")
    output_manager.separator()

    formats = converter.get_available_formats()
    for i, format_name in enumerate(formats, 1):
        info = converter.get_converter_info(format_name)
        if info:
            output_manager.format_info(f"{i}. {format_name}", info['name'])

    output_manager.info(f"\nTotal: {len(formats)} formatos disponibles")


def _show_configuration(
    converter: TIFFConverter,
    input_dir: str,
    output_dir: str,
    formats: list,
    max_workers: int,
) -> None:
    """Muestra la configuración de la conversión"""
    output_manager.section("⚙️  CONFIGURACIÓN")
    output_manager.separator()

    output_manager.format_info("📂 Directorio de entrada", input_dir)
    output_manager.format_info("📂 Directorio de salida", output_dir)
    output_manager.format_info("🔄 Formatos a convertir", formats or "Todos los habilitados")
    output_manager.format_info("👥 Workers paralelos", max_workers or "Automático")


def _show_detailed_results(result: dict) -> None:
    """Muestra resultados detallados de la conversión"""
    output_manager.section("📊 RESULTADOS DETALLADOS")
    output_manager.separator()

    output_manager.format_info("📁 Archivos procesados", result['files_processed'])
    output_manager.format_info("✅ Conversiones exitosas", result['conversions_successful'])
    output_manager.format_info("❌ Conversiones fallidas", result['conversions_failed'])
    output_manager.format_info("⏱️  Tiempo total", f"{result['time_elapsed']} segundos")
    output_manager.format_info("🔄 Formatos procesados", result['formats_processed'])


if __name__ == "__main__":
    main()
