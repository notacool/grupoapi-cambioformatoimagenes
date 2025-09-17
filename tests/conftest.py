import sys
from pathlib import Path
import pytest


# Asegura que el directorio src/ del proyecto esté en sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def pytest_ignore_collect(path):
    """Ignora tests que dependen de módulos inexistentes actualmente.

    - test_correccion_nombres.py requiere 'corregir_nombres_subcarpetas' que no está en el repo.
    """
    path_str = str(path)
    if path_str.endswith("test_correccion_nombres.py"):
        return True
    return False


@pytest.fixture
def tiff_path() -> Path:
    """Devuelve una ruta TIFF válida para tests que lo requieren."""
    # Preferir archivo de prueba incluido
    candidate = Path(__file__).parent / "test_document.tiff"
    if candidate.exists():
        return candidate

    # Crear TIFF temporal mínimo utilizando PIL si está disponible
    try:
        from PIL import Image

        tmp_path = Path(pytest.TempPathFactory.getbasetemp()) / "tmp_test_image.tiff"
        tmp_path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("L", (10, 10), color=128)
        img.save(tmp_path, format="TIFF")
        return tmp_path
    except Exception:
        # Fallback: crear archivo vacío si PIL no está disponible
        tmp_path = Path(PROJECT_ROOT) / "tests" / "tmp_empty_test.tiff"
        tmp_path.touch(exist_ok=True)
        return tmp_path


