# Conversor de Archivos TIFF

Un proyecto Python para convertir archivos TIFF a múltiples formatos de imagen de manera configurable, con funcionalidades avanzadas de resolución y **OCR integrado**.

## 🎯 **Objetivos Principales**

- **🖼️ JPG 400 DPI**: Alta resolución para impresión profesional
- **🖼️ JPG 200 DPI**: Resolución media para uso web y digital
- **📄 PDF con EasyOCR**: PDF con texto buscable usando reconocimiento óptico de caracteres

## 🔍 **OCR con EasyOCR**

### **EasyOCR (Local - Recomendado)**
- **Ventajas**: Fácil instalación, soporte nativo Python, múltiples idiomas
- **Idiomas**: 80+ idiomas incluyendo español e inglés
- **Uso**: Ideal para procesamiento local y archivos confidenciales
- **Instalación**: Automática, los modelos se descargan en la primera ejecución

## Características

- **Procesamiento por lotes**: Convierte todos los archivos TIFF de una carpeta
- **Conversores configurables**: Sistema modular para agregar nuevos formatos de salida
- **Múltiples resoluciones JPG**: Control preciso de DPI para diferentes usos
- **OCR integrado**: PDF con texto buscable usando EasyOCR
- **Interfaz CLI**: Fácil de usar desde la línea de comandos
- **Configuración flexible**: Archivos YAML para personalizar conversores
- **Procesamiento paralelo**: Múltiples workers para mayor velocidad

## Instalación

1. Clona o descarga este proyecto
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

### 🔧 **Requisitos de OCR**

#### **EasyOCR (Incluido)**
```bash
pip install easyocr
# Los modelos se descargan automáticamente en la primera ejecución
```

## Uso

### Uso básico
```bash
python main.py --input "ruta/a/carpeta" --output "ruta/salida"
```

### Opciones disponibles
- `--input`: Carpeta con archivos TIFF a convertir
- `--output`: Carpeta de destino para las conversiones
- `--formats`: Formatos específicos a convertir (ej: jpg_400,jpg_200,pdf_easyocr)
- `--config`: Archivo de configuración personalizado
- `--workers`: Número máximo de workers para procesamiento paralelo

### Ejemplos
```bash
# Convertir a todos los formatos configurados
python main.py --input "imagenes/" --output "convertidas/"

# Convertir solo a JPG de alta resolución y PDF con OCR
python main.py --input "imagenes/" --output "convertidas/" --formats jpg_400,pdf_easyocr

# Usar configuración personalizada
python main.py --input "imagenes/" --output "convertidas/" --config "mi_config.yaml"

# Ver información del conversor
python main.py --info

# Listar formatos disponibles
python main.py --list-formats
```

## Configuración

El archivo `config.yaml` permite personalizar:

### Formatos de Salida

#### JPG 400 DPI (Alta Resolución)
```yaml
jpg_400:
  enabled: true
  quality: 95          # Calidad máxima para impresión
  optimize: true
  progressive: false
  dpi: 400            # Resolución para impresión profesional
```

#### JPG 200 DPI (Resolución Media)
```yaml
jpg_200:
  enabled: true
  quality: 90          # Calidad media para web
  optimize: true
  progressive: false
  dpi: 200            # Resolución para uso digital
```

#### PDF con EasyOCR
```yaml
pdf_easyocr:
  enabled: true
  resolution: 300      # Resolución en DPI
  ocr_language: ["es", "en"]  # Lista de idiomas
  ocr_confidence: 0.5  # Confianza (0.0-1.0)
  use_gpu: false       # Usar GPU si está disponible
  create_searchable_pdf: true  # PDF con texto buscable
```

### Procesamiento
```yaml
processing:
  max_workers: 4       # Workers paralelos
  batch_size: 10       # Tamaño del lote
  overwrite_existing: false
```

## Estructura del Proyecto

```
├── main.py                 # Punto de entrada principal
├── src/
│   ├── __init__.py
│   ├── converter.py        # Motor de conversión principal
│   ├── converters/         # Módulos de conversores
│   │   ├── __init__.py
│   │   ├── base.py         # Clase base para conversores
│   │   ├── jpg_resolution_converter.py  # JPG con resolución configurable
│   │   └── pdf_easyocr_converter.py     # PDF con EasyOCR
│   ├── file_processor.py   # Procesamiento de archivos
│   └── config_manager.py   # Gestión de configuración
├── config.yaml             # Configuración por defecto
├── requirements.txt         # Dependencias
├── test_converter.py       # Script de pruebas
└── README.md               # Esta documentación
```

## 🚀 **Recomendaciones de Uso**

### **Para uso personal/pequeños proyectos:**
- **EasyOCR**: Fácil instalación, offline, buena precisión
- **Configuración**: Habilitar solo `pdf_easyocr` en `config.yaml`

### **Para desarrollo/pruebas:**
- **EasyOCR**: Fácil instalación, buena para prototipos
- **Configuración**: Habilitar solo `pdf_easyocr` en `config.yaml`

## 📋 **Configuración Rápida por Caso de Uso**

### **Caso 1: Solo JPG (sin OCR)**
```yaml
formats:
  jpg_400: { enabled: true }
  jpg_200: { enabled: true }
  pdf_easyocr: { enabled: false }
```

### **Caso 2: JPG + EasyOCR (recomendado)**
```yaml
formats:
  jpg_400: { enabled: true }
  jpg_200: { enabled: true }
  pdf_easyocr: { enabled: true }
```

## Agregar Nuevos Conversores

1. Crea una nueva clase que herede de `BaseConverter`
2. Implementa los métodos requeridos
3. Agrega la configuración en `config.yaml`
4. El sistema automáticamente detectará y usará el nuevo conversor

## Pruebas

Ejecuta el script de pruebas para verificar la funcionalidad:

```bash
python test_converter.py
```

## Solución de Problemas

### OCR no funciona
- **EasyOCR**: Verifica dependencias Python con `pip install easyocr`
- **Primera ejecución**: Los modelos se descargan automáticamente (puede tardar)

### Errores de memoria
- Reduce el número de workers (`--workers 2`)
- Procesa archivos en lotes más pequeños
- Verifica que haya suficiente RAM disponible

## Licencia

Este proyecto está bajo licencia MIT.

## 🚀 **Casos de Uso Típicos**

1. **Digitalización de documentos**: TIFF → PDF con OCR para archivos buscables
2. **Preparación para imprenta**: TIFF → JPG 400 DPI para máxima calidad
3. **Optimización web**: TIFF → JPG 200 DPI para sitios web
4. **Archivo maestro**: TIFF → PDF con OCR para preservar texto
5. **Procesamiento por lotes**: Convertir carpetas completas de documentos
6. **OCR offline**: Usar EasyOCR para archivos confidenciales
