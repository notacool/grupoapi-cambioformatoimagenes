# 🚀 Guía del Desarrollador - Conversor TIFF

Esta guía explica cómo modificar, extender y mantener el proyecto Conversor TIFF para futuros desarrolladores.

## 📋 **Tabla de Contenidos**

1. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
2. [Estructura de Archivos](#estructura-de-archivos)
3. [Cómo Agregar Nuevos Conversores](#cómo-agregar-nuevos-conversores)
4. [Cómo Modificar Conversores Existentes](#cómo-modificar-conversores-existentes)
5. [Sistema de Configuración](#sistema-de-configuración)
6. [Testing y Debugging](#testing-y-debugging)
7. [Flujo de Trabajo Git](#flujo-de-trabajo-git)
8. [Troubleshooting Común](#troubleshooting-común)

## 🏗️ **Arquitectura del Proyecto**

### **Patrón de Diseño**
El proyecto utiliza el **patrón Strategy** con conversores intercambiables:

```
BaseConverter (Interfaz)
├── JPGResolutionConverter (Estrategia JPG)
└── PDFEasyOCRConverter (Estrategia PDF + OCR)
```

### **Componentes Principales**
- **`converter.py`**: Orquesta la conversión y gestiona conversores
- **`config_manager.py`**: Maneja configuración YAML
- **`file_processor.py`**: Procesa archivos y genera rutas de salida
- **`converters/`**: Módulos de conversores específicos

## 📁 **Estructura de Archivos**

```
src/
├── converter.py              # Motor principal de conversión
├── config_manager.py         # Gestión de configuración
├── file_processor.py         # Procesamiento de archivos
└── converters/
    ├── __init__.py          # Exporta conversores
    ├── base.py              # Clase base abstracta
    ├── jpg_resolution_converter.py    # Conversor JPG
    └── pdf_easyocr_converter.py      # Conversor PDF + OCR
```

## 🔧 **Cómo Agregar Nuevos Conversores**

### **Paso 1: Crear la Clase del Conversor**

Crea un nuevo archivo en `src/converters/` (ej: `bmp_converter.py`):

```python
from pathlib import Path
from typing import Dict, Any
from PIL import Image
from .base import BaseConverter

class BMPConverter(BaseConverter):
    """Conversor de TIFF a BMP"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Configuración específica para BMP
        self.bit_depth = config.get('bit_depth', 24)
        self.rle_compression = config.get('rle_compression', False)
    
    def convert(self, input_path: Path, output_path: Path) -> bool:
        """Implementa la conversión TIFF → BMP"""
        try:
            # Validar entrada
            if not self.validate_input(input_path):
                return False
            
            # Crear directorio de salida
            if not self.create_output_directory(output_path):
                return False
            
            # Abrir y convertir imagen
            with Image.open(input_path) as img:
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Guardar como BMP
                img.save(output_path, 'BMP', bits=self.bit_depth)
                return True
                
        except Exception as e:
            print(f"Error convirtiendo a BMP: {str(e)}")
            return False
    
    def get_file_extension(self) -> str:
        """Retorna la extensión del formato"""
        return '.bmp'
    
    def get_output_filename(self, input_path: Path, output_dir: Path) -> Path:
        """Genera nombre de archivo de salida"""
        stem = input_path.stem
        extension = self.get_file_extension()
        
        # Crear subdirectorio específico
        format_dir = output_dir / "bmp"
        format_dir.mkdir(parents=True, exist_ok=True)
        
        return format_dir / f"{stem}{extension}"
```

### **Paso 2: Agregar al Sistema**

#### **2.1 Modificar `src/converters/__init__.py`**
```python
from .base import BaseConverter
from .jpg_resolution_converter import JPGResolutionConverter
from .pdf_easyocr_converter import PDFEasyOCRConverter
from .bmp_converter import BMPConverter  # ← Agregar esta línea

__all__ = [
    'BaseConverter',
    'JPGResolutionConverter', 
    'PDFEasyOCRConverter',
    'BMPConverter'  # ← Agregar esta línea
]
```

#### **2.2 Modificar `src/converter.py`**
En el método `_initialize_converters()`:

```python
def _initialize_converters(self) -> Dict[str, BaseConverter]:
    converters = {}
    
    # JPG Converters
    if self.config_manager.is_format_enabled('jpg_400'):
        jpg_400_config = self.config_manager.get_format_config('jpg_400')
        converters['jpg_400'] = JPGResolutionConverter(jpg_400_config)
    
    if self.config_manager.is_format_enabled('jpg_200'):
        jpg_200_config = self.config_manager.get_format_config('jpg_200')
        converters['jpg_200'] = JPGResolutionConverter(jpg_200_config)
    
    # PDF EasyOCR Converter
    if self.config_manager.is_format_enabled('pdf_easyocr'):
        pdf_config = self.config_manager.get_format_config('pdf_easyocr')
        converters['pdf_easyocr'] = PDFEasyOCRConverter(pdf_config)
    
    # BMP Converter ← Agregar esta sección
    if self.config_manager.is_format_enabled('bmp'):
        bmp_config = self.config_manager.get_format_config('bmp')
        converters['bmp'] = BMPConverter(bmp_config)
    
    return converters
```

#### **2.3 Modificar `src/file_processor.py`**
En el método `create_output_structure()`:

```python
def create_output_structure(self, output_dir: Path) -> None:
    """Crea la estructura de directorios de salida"""
    # Directorios existentes
    (output_dir / "jpg_400").mkdir(parents=True, exist_ok=True)
    (output_dir / "jpg_200").mkdir(parents=True, exist_ok=True)
    (output_dir / "pdf_easyocr").mkdir(parents=True, exist_ok=True)
    
    # Nuevo directorio para BMP ← Agregar esta línea
    (output_dir / "bmp").mkdir(parents=True, exist_ok=True)
```

En el método `get_output_path()`:

```python
def get_output_path(self, input_path: Path, format_name: str) -> Path:
    """Genera la ruta de salida para un formato específico"""
    if format_name == 'jpg_400':
        return self.output_dir / "jpg_400" / f"{input_path.stem}_400dpi.jpg"
    elif format_name == 'jpg_200':
        return self.output_dir / "jpg_200" / f"{input_path.stem}_200dpi.jpg"
    elif format_name == 'pdf_easyocr':
        return self.output_dir / "pdf_easyocr" / f"{input_path.stem}_EasyOCR.pdf"
    elif format_name == 'bmp':  # ← Agregar esta sección
        return self.output_dir / "bmp" / f"{input_path.stem}.bmp"
    else:
        raise ValueError(f"Formato no soportado: {format_name}")
```

### **Paso 3: Agregar Configuración**

En `config.yaml`:

```yaml
formats:
  # ... formatos existentes ...
  
  bmp:
    enabled: true
    bit_depth: 24
    rle_compression: false
```

### **Paso 4: Actualizar Tests**

En `test_converter.py`:

```python
def test_bmp_converter(self):
    """Test del conversor BMP"""
    # Configurar conversor BMP
    bmp_config = {
        'enabled': True,
        'bit_depth': 24,
        'rle_compression': False
    }
    
    # Crear conversor
    bmp_converter = BMPConverter(bmp_config)
    
    # Test de conversión
    input_path = Path("test_input/test.tiff")
    output_path = Path("test_output/test.bmp")
    
    success = bmp_converter.convert(input_path, output_path)
    self.assertTrue(success)
    self.assertTrue(output_path.exists())
```

## 🔄 **Cómo Modificar Conversores Existentes**

### **Ejemplo: Modificar JPG Resolution Converter**

#### **1. Agregar Nueva Configuración**
En `config.yaml`:
```yaml
jpg_400:
  enabled: true
  quality: 95
  optimize: true
  progressive: false
  dpi: 400
  # Nueva configuración
  sharpen: true        # ← Nueva opción
  sharpen_factor: 1.2  # ← Nueva opción
```

#### **2. Modificar el Conversor**
En `src/converters/jpg_resolution_converter.py`:

```python
def __init__(self, config: Dict[str, Any]):
    super().__init__(config)
    # Configuración existente
    self.quality = config.get('quality', 95)
    self.optimize = config.get('optimize', True)
    self.progressive = config.get('progressive', False)
    self.dpi = config.get('dpi', 300)
    
    # Nueva configuración ← Agregar estas líneas
    self.sharpen = config.get('sharpen', False)
    self.sharpen_factor = config.get('sharpen_factor', 1.0)

def convert(self, input_path: Path, output_path: Path) -> bool:
    try:
        # ... código existente ...
        
        with Image.open(input_path) as img:
            # ... código existente ...
            
            # Nueva funcionalidad de sharpening ← Agregar esta sección
            if self.sharpen:
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(self.sharpen_factor)
            
            # ... resto del código existente ...
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
```

## ⚙️ **Sistema de Configuración**

### **Estructura de Configuración**
```yaml
# config.yaml
formats:
  jpg_400:
    enabled: true
    quality: 95
    dpi: 400
  
  pdf_easyocr:
    enabled: true
    resolution: 300
    ocr_language: ["es", "en"]
    ocr_confidence: 0.5

processing:
  max_workers: 4
  batch_size: 10
  overwrite_existing: false
```

### **Acceso a Configuración en Conversores**
```python
class MyConverter(BaseConverter):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Acceder a configuración
        self.my_setting = config.get('my_setting', 'default_value')
        
        # Validar configuración requerida
        if 'required_setting' not in config:
            raise ValueError("required_setting es obligatorio")
```

## 🧪 **Testing y Debugging**

### **Ejecutar Tests**
```bash
# Test completo
python test_converter.py

# Test específico
python -m pytest test_converter.py::TestTIFFConverter::test_jpg_converter

# Test con verbose
python test_converter.py -v
```

### **Crear Tests para Nuevos Conversores**
```python
def test_my_converter_validation(self):
    """Test de validación del conversor"""
    converter = MyConverter({'enabled': True})
    
    # Test con archivo válido
    valid_file = Path("test_input/valid.tiff")
    self.assertTrue(converter.validate_input(valid_file))
    
    # Test con archivo inválido
    invalid_file = Path("test_input/invalid.txt")
    self.assertFalse(converter.validate_input(invalid_file))

def test_my_converter_output_structure(self):
    """Test de estructura de salida"""
    converter = MyConverter({'enabled': True})
    
    input_path = Path("test_input/test.tiff")
    output_dir = Path("test_output")
    
    output_path = converter.get_output_filename(input_path, output_dir)
    
    # Verificar que se crea el subdirectorio correcto
    expected_dir = output_dir / "my_format"
    self.assertTrue(expected_dir.exists())
    
    # Verificar nombre del archivo
    self.assertEqual(output_path.name, "test.my_extension")
```

### **Debugging Conversores**
```python
import logging

# Configurar logging detallado
logging.basicConfig(level=logging.DEBUG)

class MyConverter(BaseConverter):
    def convert(self, input_path: Path, output_path: Path) -> bool:
        logging.debug(f"Convirtiendo {input_path} a {output_path}")
        
        try:
            # Tu código aquí
            logging.debug("Conversión exitosa")
            return True
        except Exception as e:
            logging.error(f"Error en conversión: {str(e)}")
            return False
```

## 🔀 **Flujo de Trabajo Git**

### **1. Crear Rama de Desarrollo**
```bash
git checkout -b feature/nuevo-conversor
```

### **2. Hacer Cambios**
```bash
# Editar archivos
git add src/converters/nuevo_converter.py
git add src/converters/__init__.py
git add src/converter.py
git add config.yaml
git add test_converter.py
```

### **3. Commit y Push**
```bash
git commit -m "Agregar nuevo conversor BMP"
git push origin feature/nuevo-conversor
```

### **4. Crear Pull Request**
- Ve a GitHub y crea un Pull Request
- Describe los cambios realizados
- Incluye tests y documentación

### **5. Merge a Main**
```bash
git checkout main
git pull origin main
git merge feature/nuevo-conversor
git push origin main
```

## 🚨 **Troubleshooting Común**

### **Error: "Module not found"**
```bash
# Verificar que estás en el directorio correcto
pwd

# Verificar que Python puede importar el módulo
python -c "from src.converters import MyConverter"
```

### **Error: "Config not found"**
```yaml
# Verificar que la configuración esté en config.yaml
formats:
  my_format:
    enabled: true  # ← Asegúrate de que esté habilitado
```

### **Error: "Output directory not found"**
```python
# Verificar que se cree el directorio en file_processor.py
def create_output_structure(self, output_dir: Path) -> None:
    # Agregar tu directorio aquí
    (output_dir / "my_format").mkdir(parents=True, exist_ok=True)
```

### **Error: "Converter not initialized"**
```python
# Verificar que el conversor se agregue en _initialize_converters()
if self.config_manager.is_format_enabled('my_format'):
    my_config = self.config_manager.get_format_config('my_format')
    converters['my_format'] = MyConverter(my_config)
```

## 📚 **Recursos Adicionales**

### **Documentación de Dependencias**
- **Pillow (PIL)**: https://pillow.readthedocs.io/
- **EasyOCR**: https://github.com/JaidedAI/EasyOCR
- **PyPDF2**: https://pypdf2.readthedocs.io/
- **ReportLab**: https://www.reportlab.com/docs/reportlab-userguide.pdf

### **Patrones de Diseño**
- **Strategy Pattern**: https://refactoring.guru/design-patterns/strategy
- **Factory Pattern**: https://refactoring.guru/design-patterns/factory-method

### **Testing en Python**
- **unittest**: https://docs.python.org/3/library/unittest.html
- **pytest**: https://docs.pytest.org/

## 🎯 **Checklist para Nuevos Conversores**

- [ ] Crear clase que herede de `BaseConverter`
- [ ] Implementar método `convert()`
- [ ] Implementar método `get_file_extension()`
- [ ] Implementar método `get_output_filename()`
- [ ] Agregar a `src/converters/__init__.py`
- [ ] Agregar a `src/converter.py`
- [ ] Agregar a `src/file_processor.py`
- [ ] Agregar configuración en `config.yaml`
- [ ] Crear tests en `test_converter.py`
- [ ] Actualizar `README.md`
- [ ] Verificar que todos los tests pasen
- [ ] Crear Pull Request

## 🤝 **Contribuir al Proyecto**

1. **Fork** el repositorio
2. **Clone** tu fork localmente
3. **Crea** una rama para tu feature
4. **Implementa** los cambios
5. **Tests** que todo funcione
6. **Commit** y **push** tus cambios
7. **Crea** un Pull Request

---

**¿Necesitas ayuda?** Revisa los tests existentes o crea un issue en GitHub.
