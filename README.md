# 🖼️ Conversor TIFF - Sistema de Conversión y Metadatos

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 🎯 Descripción

El **Conversor TIFF** es un sistema avanzado de conversión de archivos TIFF que genera múltiples formatos de salida (JPG, PDF con OCR, XML MET) con metadatos completos y organización automática de archivos. Diseñado para archivos, bibliotecas y sistemas de gestión documental.

## ✨ Características Principales

### 🔄 **Conversores de Formato**
- **JPG 400 DPI**: Alta resolución para impresión profesional
- **JPG 200 DPI**: Resolución media optimizada para web
- **PDF con EasyOCR**: Texto buscable y seleccionable con reconocimiento óptico
- **Metadatos MET**: Archivos XML con estándar MET de la Library of Congress

### 📊 **Postconversores Avanzados**
- **MET Format PostConverter**: Genera XMLs consolidados por formato que incluyen:
  - Metadatos completos de archivos TIFF originales
  - Información de archivos convertidos
  - Estructura PREMIS para preservación digital
  - Organización automática en carpetas por formato

### 🗂️ **Organización Inteligente**
- **Estructura automática de carpetas**: Cada formato se organiza en su subdirectorio
- **Nomenclatura consistente**: Patrones de nombres estandarizados
- **Metadatos integrados**: Información técnica y administrativa completa

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
  jpg_400:
    enabled: true
    quality: 95                      # Calidad de compresión (1-100)
    optimize: true                   # Optimizar archivo
    progressive: false               # JPEG progresivo
    dpi: 400                        # Resolución en DPI
  
  # Conversor JPG 200 DPI (media resolución)
  jpg_200:
    enabled: true
    quality: 90                      # Calidad de compresión (1-100)
    optimize: true                   # Optimizar archivo
    progressive: true                # JPEG progresivo
    dpi: 200                        # Resolución en DPI
  
  # Conversor PDF con EasyOCR
  pdf_easyocr:
    enabled: true
    resolution: 300                  # Resolución en DPI
    page_size: "A4"                 # Tamaño de página
    fit_to_page: true                # Ajustar imagen a la página
    ocr_language: ["es", "en"]      # Idiomas para OCR
    ocr_confidence: 0.2             # Confianza mínima para OCR
    create_searchable_pdf: true      # Crear PDF con texto buscable
    use_gpu: true                    # Usar GPU si está disponible

  # Conversor MET Metadata
  met_metadata:
    enabled: true
    include_image_metadata: true     # Incluir DPI, dimensiones, orientación
    include_file_metadata: true      # Incluir tamaño, fechas, permisos
    include_processing_info: true    # Incluir información de procesamiento
    metadata_standard: "MET"        # Estándar de metadatos
    organization: "Conversor TIFF"   # Nombre de la organización
    creator: "Sistema Automatizado"  # Creador del sistema

# Configuración de procesamiento
processing:
  max_workers: 1                     # Número máximo de workers paralelos
  batch_size: 2                      # Tamaño del lote de procesamiento
  overwrite_existing: false          # Sobrescribir archivos existentes

# Configuración de salida
output:
  create_subdirectories: true        # Crear subdirectorios por formato
  naming_pattern: "{original_name}_{format}"  # Patrón de nombres

# Configuración de postconversores
postconverters:
  met_format:
    enabled: true
    include_image_metadata: true     # Incluir metadatos de imagen
    include_file_metadata: true      # Incluir metadatos de archivo
    include_processing_info: true    # Incluir información de procesamiento
    metadata_standard: "MET"        # Estándar de metadatos
    organization: "Conversor TIFF"   # Nombre de la organización
    creator: "Sistema Automatizado"  # Creador del sistema
```

### Configuraciones Especializadas

#### Configuración para Preservación Digital
```yaml
formats:
  jpg_400:
    enabled: true
    quality: 100                     # Máxima calidad
    optimize: false                  # Sin optimización para preservación
    dpi: 400                        # Alta resolución

postconverters:
  met_format:
    enabled: true
    include_image_metadata: true     # Metadatos técnicos completos
    include_file_metadata: true      # Información de archivo completa
    metadata_standard: "MET"        # Estándar institucional
    organization: "Archivo Nacional"
    creator: "Sistema de Preservación Digital v2.0"
```

#### Configuración para Producción Web
```yaml
formats:
  jpg_200:
    enabled: true
    quality: 85                      # Calidad optimizada para web
    optimize: true                   # Optimización activa
    progressive: true                # JPEG progresivo para carga rápida
    dpi: 200                        # Resolución web estándar

  pdf_easyocr:
    enabled: true
    ocr_language: ["es", "en"]      # Múltiples idiomas
    ocr_confidence: 0.3             # Confianza media para velocidad
    create_searchable_pdf: true      # PDFs con texto buscable
```

## 🎮 Uso

### Comando Básico

```bash
python main.py --input "ruta/entrada" --output "ruta/salida" --config config.yaml
```

### Ejemplos de Uso

#### Conversión Básica
```bash
# Convertir archivos TIFF a múltiples formatos
python main.py \
  --input "C:\Documentos\TIFF" \
  --output "C:\Documentos\Convertido" \
  --config config.yaml
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
| `--input` | Directorio con archivos TIFF | ✅ |
| `--output` | Directorio de salida | ✅ |
| `--config` | Archivo de configuración | ❌ (usa `config.yaml` por defecto) |
| `--info` | Mostrar información del sistema | ❌ |

## 📁 Estructura de Salida

El sistema genera una estructura organizada automáticamente:

```
directorio_salida/
├── jpg_400/                        # JPGs de 400 DPI
│   ├── documento1_400dpi.jpg
│   ├── documento2_400dpi.jpg
│   └── jpg_400.xml                # ← Metadatos consolidados
├── jpg_200/                        # JPGs de 200 DPI
│   ├── documento1_200dpi.jpg
│   ├── documento2_200dpi.jpg
│   └── jpg_200.xml                # ← Metadatos consolidados
├── pdf_easyocr/                    # PDFs con OCR
│   ├── documento1_EasyOCR.pdf
│   ├── documento2_EasyOCR.pdf
│   └── pdf_easyocr.xml            # ← Metadatos consolidados
└── met_metadata/                   # Metadatos individuales
    ├── documento1_MET.xml
    └── documento2_MET.xml
```

### Archivos XML MET Consolidados

Cada formato genera un archivo XML que incluye:

- **Metadatos de archivos TIFF originales**: DPI, dimensiones, fechas, checksum
- **Metadatos de archivos convertidos**: Tamaño, formato, ubicación
- **Información PREMIS**: Estándar para preservación digital
- **Trazabilidad completa**: Desde el original hasta cada formato generado

## 🔧 Características Técnicas

### Procesamiento Paralelo
- **Multi-threading**: Conversiones simultáneas para mayor velocidad
- **Configuración flexible**: Número de workers ajustable
- **Gestión de memoria**: Procesamiento por lotes para archivos grandes

### Validación y Calidad
- **Validación de entrada**: Verificación de archivos TIFF válidos
- **Control de calidad**: Parámetros ajustables para cada formato
- **Manejo de errores**: Recuperación robusta ante fallos

### Metadatos Avanzados
- **Estándar MET**: Cumple con METS de la Library of Congress
- **PREMIS 3.0**: Implementación completa del estándar de preservación
- **Checksums MD5**: Verificación de integridad de archivos
- **Información EXIF**: Metadatos de imagen y orientación

## 📊 Casos de Uso

### 🏛️ Archivos y Bibliotecas
- **Preservación Digital**: Metadatos completos para archivos históricos
- **Catálogos**: Información estructurada para sistemas de búsqueda
- **Compliance**: Cumplimiento de estándares institucionales

### 💼 Gestión Documental
- **Sistemas DMS**: Integración con sistemas de gestión documental
- **Workflows**: Trazabilidad completa del procesamiento
- **Auditoría**: Registro detallado de conversiones

### 🔍 Investigación y Análisis
- **Machine Learning**: Datos estructurados para entrenamiento de IA
- **Big Data**: Metadatos consistentes para análisis a gran escala
- **Investigación**: Metadatos técnicos para análisis de imágenes

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

1. **Error de Context Manager**:
   ```
   'Image' object does not support the context manager protocol
   ```
   **Solución**: El sistema ya está corregido, usar versión actualizada

2. **Archivos no van a carpetas correctas**:
   **Solución**: Verificar que `create_subdirectories: true` esté en la configuración

3. **XMLs no se generan**:
   **Solución**: Verificar que `postconverters.met_format.enabled: true`

4. **Error de permisos**:
   **Solución**: Verificar permisos de escritura en el directorio de salida

### Logs y Debug

El sistema incluye logging detallado con niveles configurables:

```bash
# Ver logs detallados
python main.py --input "entrada" --output "salida" --verbose
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
