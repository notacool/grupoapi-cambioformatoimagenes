# 🚀 Developer Guide - Conversor TIFF

## 📋 Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Patrones de Desarrollo](#patrones-de-desarrollo)
3. [Conversores](#conversores)
4. [Postconversores](#postconversores)
5. [Configuración](#configuración)
6. [Extensibilidad](#extensibilidad)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

## 🏗️ Arquitectura del Sistema

El sistema de conversión TIFF está diseñado con una arquitectura modular y extensible:

```
src/
├── converter.py              # Motor principal de conversión
├── config_manager.py         # Gestor de configuración
├── file_processor.py         # Procesador de archivos
├── output_manager.py         # Gestor de salida y logging
├── config_builder.py         # Builder pattern para configuraciones
├── converters/               # Conversores de formato
│   ├── base.py              # Clase base para conversores
│   ├── factory.py           # Factory pattern para conversores
│   ├── compression_strategies.py  # Strategy pattern para compresión
│   ├── jpg_resolution_converter.py
│   ├── pdf_easyocr_converter.py
│   └── met_metadata_converter.py
├── postconverters/           # Postprocesadores
│   ├── base.py              # Clase base para postconversores
│   └── met_format_postconverter.py
├── observers/                # Sistema de eventos
│   └── event_system.py      # Observer pattern para eventos
└── commands/                 # Sistema de comandos
    └── command_pattern.py   # Command pattern para operaciones
```

## 🏗️ Patrones de Desarrollo

El sistema implementa varios patrones de diseño para mejorar la mantenibilidad, extensibilidad y robustez:

### 🔧 Factory Pattern

**Ubicación**: `src/converters/factory.py`

Permite crear conversores de manera dinámica y registrar nuevos conversores sin modificar el código principal.

```python
from src.converters.factory import ConverterFactory

# Registrar nuevo conversor
ConverterFactory.register_converter("WEBP", WebPConverter)

# Crear conversores automáticamente
converters = ConverterFactory.create_converters_from_config(config_manager)
```

**Beneficios**:
- ✅ Extensibilidad sin modificar código existente
- ✅ Creación automática basada en configuración
- ✅ Validación de tipos de conversores

### 🎯 Strategy Pattern

**Ubicación**: `src/converters/compression_strategies.py`

Permite intercambiar diferentes estrategias de compresión de PDF dinámicamente.

```python
from src.converters.compression_strategies import CompressionContext, PikepdfCompressionStrategy

# Crear contexto con estrategia
context = CompressionContext(PikepdfCompressionStrategy())

# Cambiar estrategia dinámicamente
context.set_strategy(GhostscriptCompressionStrategy())

# Comprimir con estrategia actual
context.compress(input_path, output_path, config)
```

**Estrategias disponibles**:
- `GhostscriptCompressionStrategy`: Compresión con Ghostscript
- `PikepdfCompressionStrategy`: Compresión con pikepdf
- `PypdfCompressionStrategy`: Compresión con pypdf

### 👁️ Observer Pattern

**Ubicación**: `src/observers/event_system.py`

Sistema de eventos desacoplado para notificaciones y monitoreo.

```python
from src.observers.event_system import event_manager, LoggingObserver, MetricsObserver

# Adjuntar observadores
event_manager.attach(LoggingObserver())
event_manager.attach(MetricsObserver())

# Emitir eventos
event_manager.emit(EventType.CONVERSION_STARTED, {"file": "test.tiff"})
```

**Tipos de eventos**:
- `CONVERSION_STARTED`: Inicio de conversión
- `CONVERSION_COMPLETED`: Conversión completada
- `CONVERSION_FAILED`: Conversión fallida
- `FILE_PROCESSED`: Archivo procesado
- `ERROR_OCCURRED`: Error ocurrido

### 🏗️ Builder Pattern

**Ubicación**: `src/config_builder.py`

Construcción fluida y validada de configuraciones del sistema.

```python
from src.config_builder import ProductionConfigBuilder

# Configuración de producción
config = (ProductionConfigBuilder()
          .add_format("JPGHIGH")
          .set_format_quality(95)
          .set_format_dpi(400)
          .add_pdf_config(resolution=300)
          .set_pdf_max_size(5000)
          .build())
```

**Builders especializados**:
- `ProductionConfigBuilder`: Configuración optimizada para producción
- `DevelopmentConfigBuilder`: Configuración para desarrollo y testing

### 🔄 Command Pattern

**Ubicación**: `src/commands/command_pattern.py`

Encapsula operaciones del sistema permitiendo deshacer/rehacer.

```python
from src.commands.command_pattern import CommandInvoker, ConvertFileCommand

# Crear y ejecutar comandos
invoker = CommandInvoker()
command = ConvertFileCommand(converter, input_path, output_path, "PDF")
invoker.execute_command(command)

# Deshacer último comando
invoker.undo_last_command()
```

**Comandos disponibles**:
- `ConvertFileCommand`: Conversión de archivos
- `CreateDirectoryCommand`: Creación de directorios
- `DeleteFileCommand`: Eliminación de archivos
- `MacroCommand`: Comandos compuestos

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
        
        # 🆕 Configuración de compresión integrada
        compression_config = config.get("compression", {})
        self.pdf_compressor = PDFCompressor(compression_config)
        
        # Parámetros de compresión embebida
        self.embed_target_dpi = compression_config.get(
            "target_dpi", config.get("resolution", 300)
        )
        self.embed_image_quality = compression_config.get("image_quality", 85)
```

### 🆕 Control de OCR - Nueva Funcionalidad

El sistema ahora incluye control granular del OCR para optimizar el rendimiento:

#### **Configuración de OCR**

```python
class PDFEasyOCRConverter(BaseConverter):
    def __init__(self, config):
        # Configuración existente...
        self.create_searchable_pdf = config.get("create_searchable_pdf", True)
        self.use_ocr = config.get("use_ocr", True)  # 🆕 Nueva opción
        
        # Solo inicializar EasyOCR si está habilitado
        if self.use_ocr and self.create_searchable_pdf:
            self._initialize_easyocr()
        else:
            output_manager.info("ℹ️ OCR deshabilitado - PDFs se crearán sin texto buscable")
            self.ocr_reader = None
```

#### **Lógica de Procesamiento**

```python
def _create_pdf_with_easyocr(self, input_path: Path, output_path: Path) -> bool:
    # ... código de creación de PDF ...
    
    # Realizar OCR solo si está habilitado
    if self.use_ocr and self.create_searchable_pdf and self.ocr_reader:
        self._add_text_layer_to_pdf(canvas_obj, pil_img, scale, x, y)
    elif not self.use_ocr:
        output_manager.info(f"ℹ️ OCR deshabilitado para {input_path.name} - PDF sin texto buscable")
```

#### **Configuración en YAML**

```yaml
# Para PDFs individuales
formats:
  PDF:
    use_ocr: true                    # Habilitar OCR (por defecto)
    create_searchable_pdf: true      # Crear PDF buscable

# Para PDFs consolidados
postconverters:
  consolidated_pdf:
    use_ocr: true                    # Habilitar OCR en consolidación
```

#### **Ventajas del Control de OCR**

- **Rendimiento**: `use_ocr: false` elimina la carga de EasyOCR
- **Memoria**: Reduce uso de RAM al no cargar modelos de OCR
- **Velocidad**: Procesamiento más rápido para imágenes sin texto
- **Flexibilidad**: Control granular por conversor y postconversor

### 🆕 Sistema de Compresión de PDF

El sistema incluye un **PDFCompressor** independiente que proporciona compresión inteligente:

#### **Arquitectura de Compresión**

```python
class PDFCompressor:
    def __init__(self, config):
        self.enabled = config.get("enabled", True)
        self.compression_level = config.get("compression_level", "ebook")
        self.target_dpi = config.get("target_dpi", 200)
        self.image_quality = config.get("image_quality", 85)
        self.remove_metadata = config.get("remove_metadata", True)
        self.fallback_on_error = config.get("fallback_on_error", True)
    
    def compress(self, input_path: Path, output_path: Path) -> bool:
        # 1. Intentar compresión con pikepdf
        # 2. Fallback a pypdf si falla
        # 3. Usar archivo original si todo falla
```

#### **Doble Nivel de Compresión**

1. **Compresión Embebida** (Durante la generación):
```python
# En PDFEasyOCRConverter._create_pdf_with_easyocr()
with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
    # Guardar con DPI y calidad configurables
    pil_img.save(
        temp_file.name,
        format="JPEG",
        quality=int(self.embed_image_quality),  # 85 por defecto
        optimize=True,
    )
    
# Crear PDF con DPI objetivo
dpi = int(self.embed_target_dpi)  # 200 por defecto
scale_factor = 72 / dpi  # Reduce tamaño de página
```

2. **Post-Compresión** (Después de la generación):
```python
# En PDFEasyOCRConverter.convert()
if self.pdf_compressor.enabled:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_pdf_path = Path(temp_file.name)
    
    if self.pdf_compressor.compress(output_path, temp_pdf_path):
        shutil.move(temp_pdf_path, output_path)
```

#### **Herramientas de Compresión**

1. **pikepdf** (Preferida):
```python
def _compress_with_pikepdf(self, input_path, output_path):
    with pikepdf.open(input_path) as pdf:
        save_options = {
            "object_stream_mode": pikepdf.ObjectStreamMode.generate,
            "compress_streams": True,
            "preserve_pdfa": False,
        }
        if self.remove_metadata:
            pdf.docinfo.clear()
        pdf.save(output_path, **save_options)
```

2. **pypdf** (Fallback):
```python
def _compress_with_pypdf(self, input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
    
    writer.add_metadata({})  # Metadatos mínimos
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
```

#### **Integración en Postconversores**

```python
# En ConsolidatedPDFPostconverter
class ConsolidatedPDFPostconverter(BasePostConverter):
    def __init__(self, config):
        # ... configuración existente ...
        
        # 🆕 Compresor para PDFs consolidados
        compression_config = config.get("compression", {})
        self.pdf_compressor = PDFCompressor(compression_config)
    
    def _create_single_pdf(self, tiff_files, output_dir, subfolder_name):
        # ... generar PDF consolidado ...
        
        # Aplicar compresión al PDF consolidado
        if self.pdf_compressor.enabled:
            # Comprimir usando archivo temporal
            if self.pdf_compressor.compress(output_file, temp_pdf_path):
                shutil.move(temp_pdf_path, output_file)
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

#### Método 1: Usando Factory Pattern (Recomendado)

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

2. **Registrar en el Factory**:
```python
from src.converters.factory import ConverterFactory

# Registrar nuevo conversor
ConverterFactory.register_converter("mi_formato", MiConversor)
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

#### Método 2: Registro Manual (Método Legacy)

1. **Heredar de BaseConverter** (igual que arriba)

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

### Crear una Nueva Estrategia de Compresión

1. **Implementar CompressionStrategy**:
```python
from src.converters.compression_strategies import CompressionStrategy

class MiEstrategiaCompresion(CompressionStrategy):
    def compress(self, input_path: Path, output_path: Path, config: Dict[str, Any]) -> bool:
        # Implementar lógica de compresión
        pass
    
    def get_name(self) -> str:
        return "mi_estrategia"
```

2. **Registrar en el Factory**:
```python
from src.converters.compression_strategies import CompressionStrategyFactory

# Registrar nueva estrategia
CompressionStrategyFactory._strategies['mi_estrategia'] = MiEstrategiaCompresion
```

### Crear un Nuevo Observador

1. **Implementar Observer**:
```python
from src.observers.event_system import Observer, Event

class MiObservador(Observer):
    def update(self, event: Event) -> None:
        # Procesar evento
        if event.event_type == EventType.CONVERSION_STARTED:
            # Lógica específica
            pass
```

2. **Adjuntar al EventManager**:
```python
from src.observers.event_system import event_manager

# Adjuntar observador
event_manager.attach(MiObservador())
```

### Crear un Nuevo Comando

1. **Implementar Command**:
```python
from src.commands.command_pattern import Command

class MiComando(Command):
    def execute(self) -> bool:
        # Implementar lógica del comando
        pass
    
    def undo(self) -> bool:
        # Implementar lógica de deshacer
        pass
    
    def get_description(self) -> str:
        return "Descripción del comando"
```

2. **Usar con CommandInvoker**:
```python
from src.commands.command_pattern import CommandInvoker

invoker = CommandInvoker()
comando = MiComando()
invoker.execute_command(comando)
```

## 🎯 Mejores Prácticas con Patrones

### Configuración Dinámica

Usar el Builder Pattern para crear configuraciones específicas:

```python
from src.config_builder import ProductionConfigBuilder, DevelopmentConfigBuilder

# Configuración para producción
prod_config = ProductionConfigBuilder().build_production_config()

# Configuración para desarrollo
dev_config = DevelopmentConfigBuilder().build_development_config()

# Guardar configuración
prod_config.save_to_file("config_production.yaml")
```

### Manejo de Eventos

Implementar observadores para monitoreo y logging:

```python
from src.observers.event_system import event_manager, LoggingObserver, MetricsObserver

# Configurar observadores
event_manager.attach(LoggingObserver("conversion.log"))
event_manager.attach(MetricsObserver())

# Emitir eventos durante la conversión
event_manager.emit(EventType.CONVERSION_STARTED, {
    "input_dir": str(input_dir),
    "output_dir": str(output_dir),
    "total_files": len(files)
})
```

### Compresión Robusta

Usar Strategy Pattern para fallback automático:

```python
from src.converters.compression_strategies import CompressionContext, CompressionStrategyFactory

# Crear contexto con estrategia principal
context = CompressionContext(CompressionStrategyFactory.create_strategy("pikepdf"))

# Intentar compresión con fallback
success = context.compress(input_path, output_path, config)
if not success:
    # Fallback a Ghostscript
    context.set_strategy(CompressionStrategyFactory.create_strategy("ghostscript"))
    success = context.compress(input_path, output_path, config)
```

### Operaciones Reversibles

Usar Command Pattern para operaciones críticas:

```python
from src.commands.command_pattern import CommandInvoker, MacroCommand

# Crear macro de operaciones
commands = [
    CreateDirectoryCommand(output_dir),
    ConvertFileCommand(converter, input_file, output_file, "PDF"),
    CreateDirectoryCommand(met_dir)
]

macro = MacroCommand(commands, "Conversión completa")
invoker = CommandInvoker()
invoker.execute_command(macro)

# Si algo falla, deshacer todo
if not macro.success:
    invoker.undo_last_command()
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

## 🔄 Migración y Compatibilidad

### Migración a Patrones de Diseño

El sistema mantiene compatibilidad hacia atrás mientras introduce los nuevos patrones:

#### Migración Gradual de Conversores

```python
# Método Legacy (sigue funcionando)
def _initialize_converters(self):
    converters = {}
    if self.config_manager.is_format_enabled("JPGHIGH"):
        converters["JPGHIGH"] = JPGResolutionConverter(config)
    return converters

# Método Nuevo (recomendado)
def _initialize_converters(self):
    return ConverterFactory.create_converters_from_config(self.config_manager)
```

#### Migración de Configuración

```python
# Configuración Legacy (YAML estático)
config = ConfigManager("config.yaml")

# Configuración Dinámica (recomendado)
config = ProductionConfigBuilder().build_production_config()
```

#### Migración de Compresión

```python
# Compresión Legacy
compressor = PDFCompressor(config)
success = compressor.compress(input_path, output_path)

# Compresión con Strategy (recomendado)
context = CompressionContext(PikepdfCompressionStrategy())
success = context.compress(input_path, output_path, config)
```

### Compatibilidad de Versiones

| Versión | Patrones Disponibles | Compatibilidad |
|---------|---------------------|----------------|
| **v1.x** | Sin patrones | ✅ Total |
| **v2.x** | Factory, Strategy | ✅ Total |
| **v3.x** | + Observer, Builder | ✅ Total |
| **v4.x** | + Command | ✅ Total |

### Guía de Migración por Componente

#### 1. Conversores
- **Antes**: Registro manual en `converter.py`
- **Después**: Registro automático con `ConverterFactory`
- **Beneficio**: Extensibilidad sin modificar código principal

#### 2. Compresión
- **Antes**: Una sola estrategia de compresión
- **Después**: Múltiples estrategias con fallback
- **Beneficio**: Mayor robustez y flexibilidad

#### 3. Configuración
- **Antes**: Archivos YAML estáticos
- **Después**: Construcción dinámica con validación
- **Beneficio**: Configuraciones especializadas y validadas

#### 4. Logging
- **Antes**: Logging directo con `output_manager`
- **Después**: Sistema de eventos con observadores
- **Beneficio**: Logging estructurado y extensible

#### 5. Operaciones
- **Antes**: Operaciones directas sin reversibilidad
- **Después**: Comandos encapsulados con deshacer/rehacer
- **Beneficio**: Operaciones seguras y auditables

## 🧪 Testing

### Ejecutar Tests

```bash
# Tests básicos de import
python test_basic.py

# 🆕 Tests de compresión PDF
python test_compression.py

# 🆕 Tests de conversor PDF con compresión
python test_pdf_compression.py

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

5. **🆕 Compresión de PDF falla**:
   ```
   ⚠️ Error con pikepdf: [error message]
   ⚠️ Compresión falló, copiando archivo original
   ```
   **Comportamiento esperado**: El sistema usa fallback automático
   **Verificar**: 
   ```python
   # En configuración
   compression:
     fallback_on_error: true  # Debe estar habilitado
   ```

6. **🆕 PDFs muy grandes sin compresión**:
   **Solución**: Verificar configuración de compresión embebida
   ```yaml
   PDF:
     compression:
       enabled: true
       target_dpi: 200        # Reducir si es muy alto
       image_quality: 85      # Reducir si es muy alto
   ```

7. **🆕 Herramientas de compresión no detectadas**:
   ```
   ⚠️ No se encontraron herramientas de compresión PDF
   ```
   **Solución**: Instalar dependencias
   ```bash
   pip install pypdf pikepdf
   ```

### Troubleshooting de Patrones de Diseño

#### Factory Pattern

**Error**: `Conversor 'FORMATO' no registrado en el factory`
```python
# Solución: Registrar el conversor
from src.converters.factory import ConverterFactory
ConverterFactory.register_converter("FORMATO", MiConversor)
```

**Error**: `El conversor FORMATO debe heredar de BaseConverter`
```python
# Solución: Asegurar herencia correcta
class MiConversor(BaseConverter):  # ✅ Correcto
    pass

class MiConversor:  # ❌ Incorrecto
    pass
```

#### Strategy Pattern

**Error**: `Estrategia 'estrategia' no disponible`
```python
# Solución: Verificar estrategias disponibles
from src.converters.compression_strategies import CompressionStrategyFactory
print(CompressionStrategyFactory.get_available_strategies())
```

**Error**: `Error en compresión con estrategia`
```python
# Solución: Implementar fallback
context = CompressionContext(PikepdfCompressionStrategy())
if not context.compress(input_path, output_path, config):
    context.set_strategy(GhostscriptCompressionStrategy())
    context.compress(input_path, output_path, config)
```

#### Observer Pattern

**Error**: `Error notificando a observador`
```python
# Solución: Manejar excepciones en observadores
class MiObservador(Observer):
    def update(self, event: Event) -> None:
        try:
            # Lógica del observador
            pass
        except Exception as e:
            output_manager.error(f"Error en observador: {str(e)}")
```

**Error**: `Observador no adjuntado`
```python
# Solución: Adjuntar observador antes de emitir eventos
from src.observers.event_system import event_manager
event_manager.attach(MiObservador())
event_manager.emit(EventType.CONVERSION_STARTED, data)
```

#### Builder Pattern

**Error**: `Configuración inválida`
```python
# Solución: Validar configuración paso a paso
builder = ConfigBuilder()
config = (builder
          .add_format("JPGHIGH")
          .set_format_quality(95)  # Asegurar valor válido (1-100)
          .validate()  # Validar antes de construir
          .build())
```

**Error**: `Error guardando configuración`
```python
# Solución: Verificar permisos y ruta
try:
    config.save_to_file("config.yaml")
except PermissionError:
    output_manager.error("Sin permisos para escribir archivo")
except Exception as e:
    output_manager.error(f"Error guardando: {str(e)}")
```

#### Command Pattern

**Error**: `No hay comandos para deshacer`
```python
# Solución: Verificar historial antes de deshacer
invoker = CommandInvoker()
if invoker.get_history():
    invoker.undo_last_command()
else:
    output_manager.warning("No hay comandos para deshacer")
```

**Error**: `Error deshaciendo comando`
```python
# Solución: Implementar manejo de errores en comandos
class MiComando(Command):
    def undo(self) -> bool:
        try:
            # Lógica de deshacer
            return True
        except Exception as e:
            output_manager.error(f"Error deshaciendo: {str(e)}")
            return False
   ```

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
