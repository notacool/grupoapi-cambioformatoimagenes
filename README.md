# 🖼️ Conversor TIFF - Sistema de Conversión y Metadatos v2.0

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 🎯 Descripción

El **Conversor TIFF v2.0** es un sistema avanzado de conversión de archivos TIFF que **busca recursivamente carpetas TIFF en subcarpetas** y genera múltiples formatos de salida (JPG, PDF con OCR, XML MET) con metadatos completos y organización automática por subcarpeta. Diseñado para archivos, bibliotecas y sistemas de gestión documental con estructura organizacional compleja.

## ✨ Características Principales v2.0

### 🔄 **Procesamiento por Subcarpeta**
- **Búsqueda recursiva**: Encuentra automáticamente carpetas TIFF en subcarpetas
- **Organización automática**: Crea estructura de salida por subcarpeta
- **Procesamiento independiente**: Cada subcarpeta se procesa por separado
- **Manejo de errores**: Continúa procesando otras subcarpetas si una falla

### 🔄 **Conversores de Formato**
- **JPG 400 DPI**: Alta resolución para impresión profesional
- **JPG 200 DPI**: Resolución media optimizada para web
- **PDF con EasyOCR**: Texto buscable y seleccionable con reconocimiento óptico
- **Metadatos MET**: Archivos XML con estándar MET de la Library of Congress

### 📊 **Postconversores Avanzados por Subcarpeta**
- **Consolidated PDF PostConverter** (SE EJECUTA PRIMERO): Consolida todas las imágenes TIFF en PDFs únicos **por cada subcarpeta**:
  - **Consolidación inteligente**: Une todas las imágenes TIFF en uno o varios PDFs
  - **División por tamaño**: Divide automáticamente si excede el tamaño máximo configurable
  - **OCR integrado**: Aplica reconocimiento óptico de caracteres usando EasyOCR
  - **Ordenamiento alfabético**: Ordena archivos por nombre para secuencia correcta
  - **Nomenclatura automática**: `subcarpeta_consolidated.pdf` o `subcarpeta_01.pdf`, `subcarpeta_02.pdf`

- **MET Format PostConverter** (SE EJECUTA DESPUÉS): Genera XMLs consolidados por formato **por cada subcarpeta**:
  - **Archivo METS del TIFF original**: Documentación completa del archivo fuente por subcarpeta
  - Metadatos completos de archivos TIFF originales de la subcarpeta
  - Información de archivos convertidos de la subcarpeta
  - Estructura PREMIS para preservación digital
  - Organización automática en carpetas por formato por subcarpeta

### 🗂️ **Organización Inteligente por Subcarpeta**
- **Estructura automática**: Cada subcarpeta genera su propia estructura de salida
- **Nomenclatura consistente**: Patrones de nombres estandarizados por subcarpeta
- **Metadatos integrados**: Información técnica y administrativa completa por subcarpeta
- **Logs organizados**: Archivos de log separados por subcarpeta

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- Dependencias del sistema (ver sección de dependencias)

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/conversor-tiff.git
cd conversor-tiff

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python main.py --info
```

## ⚙️ Configuración

### Archivo de Configuración Principal

El sistema utiliza `config.yaml` para configurar todos los aspectos:

```yaml
# Configuración de formatos de salida
formats:
  # Conversor JPG 400 DPI (alta resolución)
  JPGHIGH:
    enabled: true
    quality: 95                      # Calidad de compresión (1-100)
    optimize: true                   # Optimizar archivo
    progressive: false               # JPEG progresivo
    dpi: 400                        # Resolución en DPI
  
  # Conversor JPG 200 DPI (media resolución)
  JPGLOW:
    enabled: true
    quality: 90                      # Calidad de compresión (1-100)
    optimize: true                   # Optimizar archivo
    progressive: false               # JPEG progresivo
    dpi: 200                        # Resolución en DPI
  
  # Conversor PDF con EasyOCR
  PDF:
    enabled: true
    resolution: 300                  # Resolución en DPI
    page_size: "A4"                 # Tamaño de página
    fit_to_page: true                # Ajustar imagen a la página
    ocr_language: ["es", "en"]      # Idiomas para OCR
    ocr_confidence: 0.2             # Confianza mínima para OCR
    create_searchable_pdf: true      # Crear PDF con texto buscable
    use_gpu: true                    # Usar GPU si está disponible

# Configuración de procesamiento
processing:
  max_workers: 1                     # Número máximo de workers paralelos
  batch_size: 2                      # Tamaño del lote de procesamiento
  overwrite_existing: false          # Sobrescribir archivos existentes

# Configuración de salida
output:
  create_subdirectories: true        # Crear subdirectorios por formato
  naming_pattern: "{original_name}"  # Patrón de nombres

# Configuración de metadatos MET
METS:
  enabled: true                      # Habilitar generación de archivos MET
  include_image_metadata: true       # Incluir DPI, dimensiones, orientación
  include_file_metadata: true        # Incluir tamaño, fechas, permisos
  include_processing_info: true      # Incluir información de procesamiento
  metadata_standard: 'MET'           # Estándar METS
  organization: 'Grupo API'          # Nombre de la organización
  creator: 'Sistema Automatizado'    # Sistema creador
  generate_all_met: false            # true: archivos con timestamp, false: un archivo por formato

# Configuración de postconversores
postconverters:
  # Postconversor para consolidar PDFs (SE EJECUTA PRIMERO)
  consolidated_pdf:
    enabled: true                    # Habilitar consolidación de PDFs
    max_size_mb: 10                 # Tamaño máximo por PDF en MB
    output_folder: "PDF"             # Carpeta de salida (misma que PDF individual)
    use_ocr: true                   # Aplicar OCR a las imágenes
    sort_by_name: true              # Ordenar archivos por nombre alfabético
  
  # Postconversor MET por formato (SE EJECUTA DESPUÉS)
  met_format:
    enabled: true                    # Habilitar generación de archivos MET por formato
    include_image_metadata: true     # Incluir metadatos técnicos de imagen
    include_file_metadata: true      # Incluir metadatos del archivo
    include_processing_info: true    # Incluir información de procesamiento
    metadata_standard: 'MET'         # Estándar METS
    organization: 'Grupo API'        # Nombre de la organización
    creator: 'Sistema Automatizado'  # Sistema creador
```

## 🎮 Uso

### Comando Básico

```bash
python main.py --input "carpeta_raiz" --output "ruta_salida" --config config.yaml
```

### Ejemplos de Uso

#### Conversión Básica por Subcarpeta
```bash
# Convertir archivos TIFF de todas las subcarpetas que contengan carpetas TIFF
python main.py \
  --input "C:\Documentos\Proyectos" \
  --output "C:\Documentos\Convertido"
```

```bash
# Convertir archivos TIFF de todas las subcarpetas que contengan carpetas TIFF el input tambien es el output
python main.py \
  --input "C:\Documentos\Proyectos"
```

#### Conversión con Formatos Específicos
```bash
# Usar solo formatos específicos
python main.py \
  --input "C:\Archivos\Originales" \
  --output "C:\Archivos\Procesados" \
  --formats JPGHIGH,PDF
```

#### Conversión con Configuración Personalizada
```bash
# Usar configuración específica
python main.py \
  --input "C:\Archivos\Originales" \
  --output "C:\Archivos\Procesados" \
  --config config_preservacion.yaml
```

#### Información del Sistema
```bash
# Ver formatos y conversores disponibles
python main.py --info

# Ver configuración actual
python main.py --config config.yaml --info
```

### Parámetros de Línea de Comandos

| Parámetro | Descripción | Obligatorio |
|-----------|-------------|-------------|
| `--input` | Directorio raíz con subcarpetas que contengan carpetas TIFF | ✅ |
| `--output` | Directorio de salida | ❌ (usa `--input` si no se especifica) |
| `--config` | Archivo de configuración | ❌ (usa `config.yaml` por defecto) |
| `--formats` | Formatos específicos a convertir | ❌ (usa todos los habilitados) |
| `--workers` | Número de workers paralelos | ❌ (usa configuración por defecto) |
| `--verbose` | Modo verbose con más información en pantalla | ❌ |
| `--info` | Mostrar información del sistema | ❌ |
| `--list-formats` | Listar formatos disponibles | ❌ |

## 📁 Estructura de Entrada y Salida

### 🆕 **Nuevo: Postconversor de PDF Consolidado**

El **Consolidated PDF Postconverter** es una funcionalidad avanzada que:

#### **Características Principales:**
- **🔄 Consolidación automática**: Une todas las imágenes TIFF de una subcarpeta en PDFs únicos
- **📏 División inteligente**: Divide automáticamente si excede el tamaño máximo configurable
- **🔍 OCR integrado**: Aplica reconocimiento óptico usando EasyOCR para PDFs buscables
- **📋 Ordenamiento**: Ordena archivos alfabéticamente por nombre para secuencia correcta
- **🏷️ Nomenclatura inteligente**: 
  - Un PDF: `subcarpeta_consolidated.pdf`
  - Múltiples PDFs: `subcarpeta_01.pdf`, `subcarpeta_02.pdf`, etc.

#### **Configuración:**
```yaml
postconverters:
  consolidated_pdf:
    enabled: true                    # ✅ Habilitar/deshabilitar
    max_size_mb: 15                 # 📏 Tamaño máximo por PDF (15 MB)
    output_folder: "PDF"             # 📁 Carpeta de salida
    use_ocr: true                   # 🔍 Aplicar OCR
    sort_by_name: true              # 📋 Ordenar alfabéticamente
```

#### **Orden de Ejecución:**
1. **Conversores individuales** (JPG, PDF, METS)
2. **🆕 Consolidated PDF Postconverter** ← **NUEVO**
3. **MET Format Postconverter**

### Estructura de Entrada
```
carpeta_raiz/
├── alicante/           # No tiene TIFF → No se procesa
└── madraza/            # Tiene TIFF → Se procesa
    └── TIFF/           # ← Carpeta con imágenes TIFF
        ├── imagen1.tiff
        └── imagen2.tiff
```

### Estructura de Salida Automática
```
directorio_salida/
├── logs/                               # Archivos de log por subcarpeta
│   ├── conversion_madraza_20250127_143022.log
│   └── conversion_20250127_143022.log
├── madraza/                            # Subcarpeta procesada
│   ├── METS/                           # Archivo METS del TIFF original
│   │   └── TIFF.xml                   # ← Documentación completa del archivo fuente
│   ├── JPGHIGH/                        # JPGs de 400 DPI + metadatos consolidados
│   │   ├── imagen1.jpg
│   │   ├── imagen2.jpg
│   │   └── JPGHIGH.xml                # ← Metadatos consolidados del formato
│   ├── JPGLOW/                         # JPGs de 200 DPI + metadatos consolidados
│   │   ├── imagen1.jpg
│   │   ├── imagen2.jpg
│   │   └── JPGLOW.xml                 # ← Metadatos consolidados del formato
│   └── PDF/                            # PDFs con OCR + metadatos consolidados
│       ├── imagen1_EasyOCR.pdf
│       ├── imagen2_EasyOCR.pdf
│       └── PDF.xml                     # ← Metadatos consolidados del formato
└── alicante/                           # No procesada (no tiene carpeta TIFF)
```

### Archivos XML MET Consolidados por Subcarpeta

El sistema genera dos tipos de archivos XML **por cada subcarpeta procesada**:

#### 1. Archivo METS del TIFF Original (`TIFF.xml`)
- **Documentación completa del archivo fuente**: Metadatos técnicos y administrativos de la subcarpeta
- **Información de preservación**: Estructura PREMIS para archivos originales de la subcarpeta
- **Trazabilidad**: Registro completo de archivos TIFF de la subcarpeta antes de la conversión

#### 2. Archivos MET por Formato (ej: `JPGHIGH.xml`)
- **Metadatos de archivos TIFF originales**: DPI, dimensiones, fechas, checksum de la subcarpeta
- **Metadatos de archivos convertidos**: Tamaño, formato, ubicación de la subcarpeta
- **Información PREMIS**: Estándar para preservación digital de la subcarpeta
- **Trazabilidad completa**: Desde el original hasta cada formato generado en la subcarpeta

## 🔧 Características Técnicas v2.0

### Procesamiento por Subcarpeta
- **Búsqueda recursiva**: Encuentra carpetas TIFF en cualquier nivel de subcarpetas
- **Procesamiento independiente**: Cada subcarpeta se procesa por separado
- **Manejo de errores robusto**: Continúa procesando otras subcarpetas si una falla
- **Estructura de salida organizada**: Cada subcarpeta genera su propia estructura

### Logging Avanzado
- **Logs por subcarpeta**: Archivos de log separados para cada subcarpeta procesada
- **Menos ruido en pantalla**: Solo se muestran mensajes importantes por defecto
- **Modo verbose**: Opción para mostrar todos los detalles en pantalla
- **Reportes de errores**: Generación automática de reportes de errores por subcarpeta

### Procesamiento Paralelo
- **Multi-threading**: Conversiones simultáneas para mayor velocidad
- **Configuración flexible**: Número de workers ajustable por subcarpeta
- **Gestión de memoria**: Procesamiento por lotes para archivos grandes

### Validación y Calidad
- **Validación de entrada**: Verificación de archivos TIFF válidos por subcarpeta
- **Control de calidad**: Parámetros ajustables para cada formato
- **Manejo de errores**: Recuperación robusta ante fallos por subcarpeta

### Metadatos Avanzados
- **Estándar MET**: Cumple con METS de la Library of Congress
- **PREMIS 3.0**: Implementación completa del estándar de preservación
- **Checksums MD5**: Verificación de integridad de archivos
- **Información EXIF**: Metadatos de imagen y orientación

## 📊 Casos de Uso

### 🏛️ Archivos y Bibliotecas
- **Preservación Digital**: Metadatos completos para archivos históricos organizados por colección
- **Catálogos**: Información estructurada para sistemas de búsqueda por subcarpeta
- **Compliance**: Cumplimiento de estándares institucionales por organización

### 💼 Gestión Documental
- **Sistemas DMS**: Integración con sistemas de gestión documental organizados por proyecto
- **Workflows**: Trazabilidad completa del procesamiento por subcarpeta
- **Auditoría**: Registro detallado de conversiones por organización

### 🔍 Investigación y Análisis
- **Machine Learning**: Datos estructurados para entrenamiento de IA por subcarpeta
- **Big Data**: Metadatos consistentes para análisis a gran escala por organización
- **Investigación**: Metadatos técnicos para análisis de imágenes por proyecto

## 🧪 Testing

### Ejecutar Tests

```bash
# Tests básicos
python test_converter.py

# Tests específicos de MET
python test_met_converter.py

# Tests consolidados
python test_consolidated_met.py
```

### Verificar Funcionamiento

```bash
# Probar con archivos de ejemplo
python main.py \
  --input "test_input" \
  --output "test_output" \
  --config config.yaml
```

## 🔍 Troubleshooting

### Problemas Comunes

1. **No se encuentran carpetas TIFF**:
   **Solución**: Verificar que existan subcarpetas con carpetas llamadas exactamente "TIFF"

2. **Archivos no van a carpetas correctas**:
   **Solución**: Verificar que `create_subdirectories: true` esté en la configuración

3. **XMLs no se generan**:
   **Solución**: Verificar que `postconverters.met_format.enabled: true`

4. **Error de permisos**:
   **Solución**: Verificar permisos de escritura en el directorio de salida

5. **Subcarpeta falla pero otras continúan**:
   **Comportamiento esperado**: El sistema continúa procesando otras subcarpetas y genera reporte de errores

### Logs y Debug

El sistema incluye logging detallado con niveles configurables:

```bash
# Ver logs detallados
python main.py --input "entrada" --output "salida" --verbose

# Los logs se guardan automáticamente en la carpeta 'logs/' del directorio de salida
```


## 📚 Documentación

- **[Developer Guide](DEVELOPER_GUIDE.md)**: Guía completa para desarrolladores
- **[MET Converter README](MET_CONVERTER_README.md)**: Documentación específica de MET
- **[Ejemplos](examples/)**: Código de ejemplo y casos de uso

## 🤝 Contribuir

1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre** un Pull Request

### Estándares de Contribución

- **Python 3.8+**: Usa type hints y f-strings
- **PEP 8**: Sigue las convenciones de estilo
- **Tests**: Agrega tests para nuevas funcionalidades
- **Documentación**: Actualiza README y Developer Guide

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- **Library of Congress**: Por el estándar METS
- **PREMIS Editorial Committee**: Por el estándar PREMIS
- **Pillow/PIL**: Por el procesamiento de imágenes
- **EasyOCR**: Por el reconocimiento óptico de caracteres
- **ReportLab**: Por la generación de PDFs

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/conversor-tiff/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tu-usuario/conversor-tiff/discussions)
- **Wiki**: [Documentación del proyecto](https://github.com/tu-usuario/conversor-tiff/wiki)

---

**⭐ Si este proyecto te es útil, ¡déjanos una estrella en GitHub!**

**🆕 Nueva en v2.0: Procesamiento por subcarpeta, logging avanzado y organización automática por organización**
