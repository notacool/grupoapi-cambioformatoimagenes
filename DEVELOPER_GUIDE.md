# 🚀 Developer Guide - Conversor TIFF

## 📋 Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Conversores](#conversores)
3. [Postconversores](#postconversores)
4. [Configuración](#configuración)
5. [Extensibilidad](#extensibilidad)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## 🏗️ Arquitectura del Sistema

El sistema de conversión TIFF está diseñado con una arquitectura modular y extensible:

```
src/
├── converter.py              # Motor principal de conversión
├── config_manager.py         # Gestor de configuración
├── file_processor.py         # Procesador de archivos
├── output_manager.py         # Gestor de salida y logging
├── converters/               # Conversores de formato
│   ├── base.py              # Clase base para conversores
│   ├── jpg_resolution_converter.py
│   ├── pdf_easyocr_converter.py
│   └── met_metadata_converter.py
└── postconverters/           # Postprocesadores
    ├── base.py              # Clase base para postconversores
    └── met_format_postconverter.py
```

## 🔄 Conversores

### Estructura Base

Todos los conversores heredan de `BaseConverter` e implementan:

- `convert(input_path, output_path)`: Método principal de conversión
- `get_file_extension()`: Extensión del archivo de salida
- `get_output_filename()`: Generación de nombres de archivo con estructura de carpetas
- `validate_input()`: Validación de archivos de entrada

### Conversor JPG

```python
class JPGResolutionConverter(BaseConverter):
    def __init__(self, config):
        self.quality = config.get("quality", 90)
        self.optimize = config.get("optimize", True)
        self.progressive = config.get("progressive", False)
        self.dpi = config.get("dpi", 200)
    
    def get_output_filename(self, input_file, output_dir):
        # Crea subdirectorio específico para este formato
        if self.dpi == 400:
            format_subdir = output_dir / "jpg_400"
        elif self.dpi == 200:
            format_subdir = output_dir / "jpg_200"
        
        format_subdir.mkdir(exist_ok=True)
        return format_subdir / f"{input_file.stem}_{self.dpi}dpi.jpg"
```

### Conversor PDF EasyOCR

```python
class PDFEasyOCRConverter(BaseConverter):
    def __init__(self, config):
        self.ocr_language = config.get("ocr_language", ["es"])
        self.create_searchable_pdf = config.get("create_searchable_pdf", True)
        self.page_size = config.get("page_size", "A4")
        self.fit_to_page = config.get("fit_to_page", True)
        self.ocr_confidence = config.get("ocr_confidence", 0.5)
        self.use_gpu = config.get("use_gpu", False)
```

## 🔄 Postconversores

### Estructura Base

Los postconversores heredan de `BasePostConverter` y se ejecutan después de la conversión principal:

```python
class BasePostConverter(ABC):
    @abstractmethod
    def process(self, conversion_result: Dict[str, Any], output_dir: Path) -> bool:
        """Procesa el resultado de la conversión"""
        pass
    
    def get_name(self) -> str:
        """Retorna el nombre del postconversor"""
        return self.__class__.__name__
```

### MET Format PostConverter

El **MET Format PostConverter** es un postconversor avanzado que genera archivos XML MET (Metadata Encoding and Transmission Standard) consolidados por formato.

#### 🎯 Funcionalidades Principales

1. **Generación de Metadatos Consolidados**: Crea un XML por formato que incluye información de todos los archivos convertidos
2. **Metadatos de TIFF Originales**: Incluye información completa de los archivos TIFF de entrada
3. **Metadatos de Archivos Convertidos**: Agrega información de los archivos generados (JPG, PDF, etc.)
4. **Estructura PREMIS**: Implementa el estándar PREMIS para preservación digital
5. **Organización por Carpetas**: Coloca los XMLs en las carpetas de formato correspondientes

#### 🏗️ Arquitectura del Postconverter

```python
class METFormatPostConverter(BasePostConverter):
    def __init__(self, config):
        self.include_image_metadata = config.get("include_image_metadata", True)
        self.include_file_metadata = config.get("include_file_metadata", True)
        self.include_processing_info = config.get("include_processing_info", True)
        self.metadata_standard = config.get("metadata_standard", "MET")
        self.organization = config.get("organization", "Conversor TIFF")
        self.creator = config.get("creator", "Sistema Automatizado")
```

#### 🔄 Flujo de Procesamiento

1. **Preparación de Datos**: `_prepare_conversion_results()`
   - Recopila información de archivos convertidos
   - Agrupa por formato de salida
   - Valida éxito de conversiones

2. **Agrupación por Formato**: `_create_format_specific_met()`
   - Organiza archivos por tipo de formato
   - Prepara datos para generación de XML

3. **Generación de XML**: `_create_single_format_met_file()`
   - Crea estructura MET estándar
   - Incluye metadatos de TIFF originales
   - Agrega información de archivos convertidos
   - Genera sección PREMIS

#### 📊 Estructura XML Generada

```xml
<?xml version="1.0" encoding="utf-8"?>
<mets xmlns="http://www.loc.gov/METS/"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  
  <!-- Información del objeto -->
  <objid>MET_JPG_400_20240827_113800</objid>
  
  <!-- Información del agente -->
  <agent ROLE="CREATOR" TYPE="ORGANIZATION">
    <name>Conversor TIFF</name>
  </agent>
  
  <!-- Encabezado METS -->
  <metsHdr CREATEDATE="2024-08-27T11:38:00" LASTMODDATE="2024-08-27T11:38:00">
    <agent ROLE="CREATOR" TYPE="OTHER" OTHERTYPE="SOFTWARE">
      <name>Sistema Automatizado</name>
    </agent>
  </metsHdr>
  
  <!-- Sección de archivos -->
  <fileSec>
    <fileGrp USE="PRESERVATION">
      <!-- Archivo TIFF original -->
      <file ID="FILE_230_1_0001_ORIGINAL" MIMETYPE="image/tiff" SIZE="86950436">
        <FLocat xlink:href="C:\...\230_1_0001.tif"/>
        <fileInfo name="230_1_0001.tif" extension=".tif" size_bytes="86950436" size_mb="82.92"/>
        <imageInfo width="3980" height="5500" mode="RGB" dpi_x="400.0" dpi_y="400.0"/>
      </file>
      
      <!-- Archivo JPG convertido -->
      <file ID="FILE_230_1_0001_JPG_400" MIMETYPE="image/jpeg" SIZE="8790294">
        <FLocat xlink:href="C:\...\230_1_0001_400dpi.jpg"/>
        <fileInfo name="230_1_0001_400dpi.jpg" extension=".jpg" size_bytes="8790294" size_mb="8.38"/>
      </file>
    </fileGrp>
  </fileSec>
  
  <!-- Metadatos administrativos PREMIS -->
  <amdSec>
    <premisMD ID="PREMIS_JPG_400">
      <mdWrap MDTYPE="PREMIS" OTHERMDTYPE="PREMIS">
        <xmlData>
          <premis xmlns="http://www.loc.gov/premis/v3" version="3.0">
            <objects>
              <object>
                <objectIdentifier>
                  <objectIdentifierValue>230_1_0001_jpg_400</objectIdentifierValue>
                  <objectIdentifierType>LOCAL</objectIdentifierType>
                </objectIdentifier>
                <objectCharacteristics>
                  <size>8790294</size>
                  <format>
                    <formatDesignation>
                      <formatName>jpg_400</formatName>
                      <formatVersion>1.0</formatVersion>
                    </formatDesignation>
                  </format>
                </objectCharacteristics>
              </object>
            </objects>
          </premis>
        </xmlData>
      </mdWrap>
    </premisMD>
  </amdSec>
</mets>
```

#### 🗂️ Organización de Archivos

El postconverter coloca los XMLs en las carpetas de formato correspondientes:

```
output_directory/
├── jpg_400/
│   ├── archivo1_400dpi.jpg
│   ├── archivo2_400dpi.jpg
│   └── jpg_400.xml          # ← XML consolidado para JPG 400 DPI
├── jpg_200/
│   ├── archivo1_200dpi.jpg
│   ├── archivo2_200dpi.jpg
│   └── jpg_200.xml          # ← XML consolidado para JPG 200 DPI
├── pdf_easyocr/
│   ├── archivo1_EasyOCR.pdf
│   ├── archivo2_EasyOCR.pdf
│   └── pdf_easyocr.xml      # ← XML consolidado para PDF EasyOCR
└── met_metadata/
    ├── archivo1_MET.xml
    └── archivo2_MET.xml
```

#### ⚙️ Configuración del Postconverter

```yaml
# En config.yaml
postconverters:
  met_format:
    enabled: true
    include_image_metadata: true
    include_file_metadata: true
    include_processing_info: true
    metadata_standard: "MET"
    organization: "Mi Organización"
    creator: "Sistema de Conversión Automatizado"
```

#### 🔧 Métodos Principales

- **`process(conversion_result, output_dir)`**: Método principal que ejecuta el postconversor
- **`_prepare_conversion_results(conversion_result)`**: Prepara los datos para generación de XML
- **`_create_format_specific_met(conversion_results, output_dir)`**: Crea XMLs por formato
- **`_create_single_format_met_file(format_type, files, output_dir)`**: Genera XML individual por formato
- **`_add_file_metadata(file_elem, input_path)`**: Agrega metadatos del archivo
- **`_add_image_metadata(file_elem, input_path)`**: Agrega metadatos de imagen
- **`_calculate_checksum(file_path)`**: Calcula checksum MD5 del archivo

#### 🎨 Personalización

El postconverter es altamente configurable:

```python
# Configuración de metadatos
self.include_image_metadata = True    # Incluir DPI, dimensiones, orientación
self.include_file_metadata = True     # Incluir tamaño, fechas, permisos
self.include_processing_info = True   # Incluir información de procesamiento

# Configuración institucional
self.organization = "Biblioteca Nacional"
self.creator = "Conversor TIFF v2.0"
self.metadata_standard = "MET"
```

#### 🚀 Casos de Uso

1. **Preservación Digital**: Metadatos completos para archivos históricos
2. **Catálogos**: Información estructurada para sistemas de búsqueda
3. **Compliance**: Cumplimiento de estándares de metadatos institucionales
4. **Auditoría**: Trazabilidad completa del procesamiento
5. **Integración**: Compatible con sistemas de gestión documental

## ⚙️ Configuración

### Archivo de Configuración Principal

```yaml
# config.yaml
formats:
  jpg_400:
    enabled: true
    quality: 95
    optimize: true
    progressive: false
    dpi: 400
  
  jpg_200:
    enabled: true
    quality: 90
    optimize: true
    progressive: true
    dpi: 200
  
  pdf_easyocr:
    enabled: true
    resolution: 300
    page_size: "A4"
    fit_to_page: true
    ocr_language: ["es", "en"]
    ocr_confidence: 0.2
    create_searchable_pdf: true
    use_gpu: true
  
  met_metadata:
    enabled: true
    include_image_metadata: true
    include_file_metadata: true
    include_processing_info: true
    metadata_standard: "MET"
    organization: "Conversor TIFF"
    creator: "Sistema Automatizado"

# Configuración de procesamiento
processing:
  max_workers: 1
  batch_size: 2
  overwrite_existing: false

# Configuración de salida
output:
  create_subdirectories: true
  naming_pattern: "{original_name}_{format}"

# Configuración de postconversores
postconverters:
  met_format:
    enabled: true
    include_image_metadata: true
    include_file_metadata: true
    include_processing_info: true
    metadata_standard: "MET"
    organization: "Conversor TIFF"
    creator: "Sistema Automatizado"
```

## 🔧 Extensibilidad

### Crear un Nuevo Conversor

1. **Heredar de BaseConverter**:
```python
from .base import BaseConverter

class MiConversor(BaseConverter):
    def convert(self, input_path: Path, output_path: Path) -> bool:
        # Implementar lógica de conversión
        pass
    
    def get_file_extension(self) -> str:
        return ".mi_formato"
    
    def get_output_filename(self, input_file: Path, output_dir: Path) -> Path:
        # Crear estructura de carpetas específica
        format_subdir = output_dir / "mi_formato"
        format_subdir.mkdir(exist_ok=True)
        return format_subdir / f"{input_file.stem}.mi_formato"
```

2. **Registrar en el conversor principal**:
```python
# En converter.py
def _initialize_converters(self):
    converters = {}
    
    # Agregar nuevo conversor
    if self.config_manager.is_format_enabled("mi_formato"):
        mi_formato_config = self.config_manager.get_format_config("mi_formato")
        converters["mi_formato"] = MiConversor(mi_formato_config)
    
    return converters
```

3. **Agregar configuración**:
```yaml
# En config.yaml
formats:
  mi_formato:
    enabled: true
    parametro1: "valor1"
    parametro2: "valor2"
```

### Crear un Nuevo Postconversor

1. **Heredar de BasePostConverter**:
```python
from .base import BasePostConverter

class MiPostconversor(BasePostConverter):
    def process(self, conversion_result: Dict[str, Any], output_dir: Path) -> bool:
        # Implementar lógica de postprocesamiento
        pass
    
    def get_name(self) -> str:
        return "Mi Postconversor"
```

2. **Registrar en el conversor principal**:
```python
# En converter.py
def _initialize_postconverters(self):
    postconverters = {}
    
    # Agregar nuevo postconversor
    if self.config_manager.is_postconverter_enabled("mi_postconversor"):
        mi_postconversor_config = self.config_manager.get_postconverter_config("mi_postconversor")
        postconverters["mi_postconversor"] = MiPostconversor(mi_postconversor_config)
    
    return postconverters
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Test básico
python test_converter.py

# Test específico de MET
python test_met_converter.py

# Test consolidado
python test_consolidated_met.py
```

### Crear Nuevos Tests

```python
# test_mi_conversor.py
import unittest
from pathlib import Path
from src.converters.mi_conversor import MiConversor

class TestMiConversor(unittest.TestCase):
    def setUp(self):
        self.config = {"parametro1": "valor1"}
        self.converter = MiConversor(self.config)
    
    def test_conversion(self):
        input_path = Path("test_input/test.tiff")
        output_path = Path("test_output/test.mi_formato")
        
        success = self.converter.convert(input_path, output_path)
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
```

## 🔍 Troubleshooting

### Problemas Comunes

1. **Error de Context Manager**:
   ```
   'Image' object does not support the context manager protocol
   ```
   **Solución**: Usar `PIL.Image.open()` en lugar de `RLImage`

2. **Archivos no van a carpetas correctas**:
   **Solución**: Implementar `get_output_filename()` que cree subdirectorios

3. **XMLs no se generan**:
   **Solución**: Verificar que el postconverter esté habilitado en la configuración

4. **Error de permisos**:
   **Solución**: Verificar permisos de escritura en el directorio de salida

### Logs y Debug

El sistema incluye logging detallado:

```python
from src.output_manager import output_manager

# Niveles de log disponibles
output_manager.info("Información general")
output_manager.success("Operación exitosa")
output_manager.warning("Advertencia")
output_manager.error("Error")
output_manager.debug("Información de debug")
```

### Verificar Configuración

```python
from src.config_manager import ConfigManager

config_manager = ConfigManager("config.yaml")
print("Formatos habilitados:", config_manager.get_enabled_formats())
print("Postconversores habilitados:", config_manager.get_enabled_postconverters())
```

## 📚 Recursos Adicionales

- [Documentación MET](https://www.loc.gov/standards/mets/)
- [Estándar PREMIS](https://www.loc.gov/standards/premis/)
- [PIL/Pillow Documentation](https://pillow.readthedocs.io/)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [EasyOCR Documentation](https://github.com/JaidedAI/EasyOCR)
