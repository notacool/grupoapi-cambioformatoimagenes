#!/usr/bin/env python3
"""
Conversor de Archivos TIFF - Punto de entrada principal
"""

import sys
import traceback
from pathlib import Path

import click

from src.converter import TIFFConverter


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
    help="Formatos específicos a convertir (ej: jpg_400,jpg_200,pdf_easyocr,met_metadata)",
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
        python main.py --input "imagenes/" --output "convertidas/" --formats jpg_400,pdf_easyocr
        python main.py --input "imagenes/" --output "convertidas/" --formats met_metadata
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
            click.echo("❌ Error: Se requieren --input y --output para la conversión")
            click.echo("   Use --help para ver todas las opciones disponibles")
            return

        # Validar directorios
        if not _validate_directories(input_dir, output_dir):
            return

        # Procesar formatos especificados
        format_list = None
        if formats:
            format_list = [f.strip().lower() for f in formats.split(",")]
            if verbose:
                click.echo(f"Formatos especificados: {format_list}")

        # Mostrar configuración si es verbose
        if verbose:
            _show_configuration(
                converter, input_dir, output_dir, format_list, max_workers
            )

        # Ejecutar conversión
        click.echo("\n🚀 Iniciando conversión de archivos TIFF...")
        result = converter.convert_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            formats=format_list,
            max_workers=max_workers,
        )

        # Mostrar resultado
        if result["success"]:
            click.echo("\n✅ Conversión completada exitosamente!")
            if verbose:
                _show_detailed_results(result)
        else:
            click.echo(f"\n❌ Error en la conversión: {result['error']}")
            sys.exit(1)

    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Conversión interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error inesperado: {str(e)}")
        if verbose:
            traceback.print_exc()
        sys.exit(1)


def _validate_directories(input_dir, output_dir):
    """Valida que los directorios sean válidos"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Validar directorio de entrada
    if not input_path.exists():
        click.echo(f"❌ Error: El directorio de entrada no existe: {input_dir}")
        return False

    if not input_path.is_dir():
        click.echo(f"❌ Error: La ruta de entrada no es un directorio: {input_dir}")
        return False

    # Validar directorio de salida
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        click.echo(f"❌ Error: No se puede crear el directorio de salida: {str(e)}")
        return False

    return True


def _show_converter_info(converter):
    """Muestra información del conversor"""
    click.echo("🔧 INFORMACIÓN DEL CONVERSOR")
    click.echo("=" * 40)

    available_formats = converter.get_available_formats()
    click.echo(f"Formatos disponibles: {', '.join(available_formats)}")

    for format_name in available_formats:
        info = converter.get_converter_info(format_name)
        if info:
            click.echo(f"\n📁 {format_name.upper()}:")
            click.echo(f"   Clase: {info['name']}")
            click.echo(f"   Extensión: {info['extension']}")
            click.echo(f"   Configuración: {info['config']}")


def _list_available_formats(converter):
    """Lista los formatos disponibles"""
    formats = converter.get_available_formats()
    click.echo("📋 FORMATOS DISPONIBLES")
    click.echo("=" * 30)

    for i, format_name in enumerate(formats, 1):
        info = converter.get_converter_info(format_name)
        if info:
            click.echo(f"{i}. {format_name.upper()} ({info['extension']})")

    if not formats:
        click.echo("No hay conversores disponibles")


def _show_configuration(converter, input_dir, output_dir, formats, max_workers):
    """Muestra la configuración actual"""
    click.echo("⚙️  CONFIGURACIÓN ACTUAL")
    click.echo("=" * 30)
    click.echo(f"Directorio de entrada: {input_dir}")
    click.echo(f"Directorio de salida: {output_dir}")
    click.echo(f"Formatos a convertir: {formats or 'Todos los habilitados'}")
    click.echo(f"Workers máximos: {max_workers or 'Por defecto'}")

    available_formats = converter.get_available_formats()
    click.echo(f"Conversores activos: {', '.join(available_formats)}")


def _show_detailed_results(result):
    """Muestra resultados detallados"""
    click.echo("\n📊 RESULTADOS DETALLADOS")
    click.echo("=" * 30)
    click.echo(f"Archivos procesados: {result['files_processed']}")
    click.echo(f"Formatos procesados: {', '.join(result['formats_processed'])}")
    click.echo(f"Conversiones exitosas: {result['conversions_successful']}")
    click.echo(f"Conversiones fallidas: {result['conversions_failed']}")
    click.echo(f"Tiempo total: {result['time_elapsed']} segundos")

    if result["conversions_successful"] > 0:
        avg_time = result["time_elapsed"] / result["conversions_successful"]
        click.echo(f"Tiempo promedio por conversión: {avg_time:.2f} segundos")


if __name__ == "__main__":
    main()
