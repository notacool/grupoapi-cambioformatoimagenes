# Conversor de Archivos TIFF

Un proyecto Python para convertir archivos TIFF a múltiples formatos de imagen de manera configurable, con funcionalidades avanzadas de resolución y **múltiples opciones de OCR**.

## 🎯 **Objetivos Principales**

- **🖼️ JPG 400 DPI**: Alta resolución para impresión profesional
- **🖼️ JPG 200 DPI**: Resolución media para uso web y digital
- **📄 PDF con OCR**: **3 opciones diferentes** para reconocimiento de texto

## 🔍 **Opciones de OCR Disponibles**

### **1. Tesseract OCR (Local - Recomendado para uso offline)**
- **Ventajas**: Gratuito, funciona offline, alta precisión
- **Desventajas**: Requiere instalación local, puede ser lento
- **Idiomas**: Español, inglés y 100+ idiomas adicionales
- **Uso**: Ideal para procesamiento local y archivos confidenciales

### **2. EasyOCR (Local - Alternativa moderna)**
- **Ventajas**: Fácil instalación, soporte nativo Python, múltiples idiomas
- **Desventajas**: Más lento que Tesseract, mayor uso de memoria
- **Idiomas**: 80+ idiomas incluyendo español e inglés
- **Uso**: Alternativa cuando Tesseract no funciona

### **3. Azure Computer Vision OCR (En la nube - Máxima precisión)**
- **Ventajas**: 99%+ precisión, soporte para texto manuscrito, escalable
- **Desventajas**: Requiere conexión a internet, costo por uso
- **Idiomas**: Soporte completo para múltiples idiomas
- **Uso**: Para proyectos profesionales y máxima calidad

## Características

- **Procesamiento por lotes**: Convierte todos los archivos TIFF de una carpeta
- **Conversores configurables**: Sistema modular para agregar nuevos formatos de salida
- **Múltiples resoluciones JPG**: Control preciso de DPI para diferentes usos
- **3 opciones de OCR**: Local y en la nube para diferentes necesidades
- **Interfaz CLI**: Fácil de usar desde la línea de comandos
- **Configuración flexible**: Archivos YAML para personalizar conversores
- **Procesamiento paralelo**: Múltiples workers para mayor velocidad

## Instalación

1. Clona o descarga este proyecto
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

### 🔧 **Requisitos de OCR por Opción**

#### **Opción 1: Tesseract OCR (Recomendado)**
**Windows:**
- Descarga desde: https://github.com/UB-Mannheim/tesseract/wiki
- Agrega Tesseract al PATH del sistema

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # Para idiomas adicionales
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-spa tesseract-ocr-eng  # Para español e inglés
```

#### **Opción 2: EasyOCR (Alternativa local)**
```bash
pip install easyocr
# Los modelos se descargan automáticamente en la primera ejecución
```

#### **Opción 3: Azure Computer Vision (En la nube)**
- Crear cuenta en Azure: https://azure.microsoft.com/
- Crear recurso Computer Vision
- Configurar credenciales en `config_azure_example.yaml`

## Uso

### Uso básico
```bash
python main.py --input "ruta/a/carpeta" --output "ruta/salida"
```

### Opciones disponibles
- `--input`: Carpeta con archivos TIFF a convertir
- `--output`: Carpeta de destino para las conversiones
- `--formats`: Formatos específicos a convertir (ej: jpg_400,jpg_200,pdf_ocr)
- `--config`: Archivo de configuración personalizado
- `--workers`: Número máximo de workers para procesamiento paralelo

### Ejemplos
```bash
# Convertir a todos los formatos configurados
python main.py --input "imagenes/" --output "convertidas/"

# Convertir solo a JPG de alta resolución y PDF con OCR
python main.py --input "imagenes/" --output "convertidas/" --formats jpg_400,pdf_ocr

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

#### PDF con Tesseract OCR (Local)
```yaml
pdf_ocr:
  enabled: true
  resolution: 300      # Resolución en DPI
  ocr_language: "spa+eng"  # Español + Inglés
  ocr_confidence: 60   # Confianza mínima para OCR (0-100)
  create_searchable_pdf: true  # PDF con texto buscable
```

#### PDF con EasyOCR (Alternativa local)
```yaml
pdf_easyocr:
  enabled: false       # Cambiar a true para usar EasyOCR
  resolution: 300
  ocr_language: ["es", "en"]  # Lista de idiomas
  ocr_confidence: 0.5  # Confianza (0.0-1.0)
  use_gpu: false       # Usar GPU si está disponible
```

#### PDF con Azure Computer Vision (En la nube)
```yaml
pdf_azure_ocr:
  enabled: false       # Cambiar a true para usar Azure
  resolution: 300
  ocr_language: "es,en"
  ocr_confidence: 0.6
  azure_subscription_key: "TU_CLAVE_AQUI"
  azure_endpoint: "https://TU_RECURSO.cognitiveservices.azure.com/"
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

│   │   ├── pdf_ocr_converter.py         # PDF con Tesseract OCR
│   │   ├── pdf_easyocr_converter.py     # PDF con EasyOCR
│   │   └── pdf_azure_ocr_converter.py   # PDF con Azure OCR
│   ├── file_processor.py   # Procesamiento de archivos
│   └── config_manager.py   # Gestión de configuración
├── config.yaml             # Configuración por defecto
├── config_azure_example.yaml  # Ejemplo para Azure OCR
├── requirements.txt         # Dependencias
├── test_converter.py       # Script de pruebas
└── README.md               # Esta documentación
```

## 🔍 **Comparación de Opciones de OCR**

| Característica | Tesseract | EasyOCR | Azure OCR |
|----------------|-----------|---------|-----------|
| **Precisión** | 95-98% | 90-95% | 99%+ |
| **Velocidad** | Media | Lenta | Rápida |
| **Costo** | Gratuito | Gratuito | Pago por uso |
| **Instalación** | Compleja | Simple | No requiere |
| **Offline** | ✅ Sí | ✅ Sí | ❌ No |
| **Idiomas** | 100+ | 80+ | Múltiples |
| **Texto manuscrito** | ❌ No | ❌ No | ✅ Sí |
| **Escalabilidad** | Limitada | Limitada | Alta |

## 🚀 **Recomendaciones de Uso**

### **Para uso personal/pequeños proyectos:**
- **Tesseract OCR**: Gratuito, offline, buena precisión
- **Configuración**: Habilitar solo `pdf_ocr` en `config.yaml`

### **Para proyectos profesionales:**
- **Azure Computer Vision**: Máxima precisión, escalable
- **Configuración**: Usar `config_azure_example.yaml` como base

### **Para desarrollo/pruebas:**
- **EasyOCR**: Fácil instalación, buena para prototipos
- **Configuración**: Habilitar solo `pdf_easyocr` en `config.yaml`

## 📋 **Configuración Rápida por Caso de Uso**

### **Caso 1: Solo JPG (sin OCR)**
```yaml
formats:
  jpg_400: { enabled: true }
  jpg_200: { enabled: true }
  pdf_ocr: { enabled: false }
  pdf_easyocr: { enabled: false }
  pdf_azure_ocr: { enabled: false }
```

### **Caso 2: JPG + Tesseract OCR (recomendado)**
```yaml
formats:
  jpg_400: { enabled: true }
  jpg_200: { enabled: true }
  pdf_ocr: { enabled: true }
  pdf_easyocr: { enabled: false }
  pdf_azure_ocr: { enabled: false }
```

### **Caso 3: JPG + Azure OCR (profesional)**
```yaml
formats:
  jpg_400: { enabled: true }
  jpg_200: { enabled: true }
  pdf_ocr: { enabled: false }
  pdf_easyocr: { enabled: false }
  pdf_azure_ocr: 
    enabled: true
    azure_subscription_key: "TU_CLAVE"
    azure_endpoint: "https://TU_RECURSO.cognitiveservices.azure.com/"
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
- **Tesseract**: Verifica instalación y PATH
- **EasyOCR**: Verifica dependencias Python
- **Azure**: Verifica credenciales y conexión a internet

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
6. **OCR de alta precisión**: Usar Azure para documentos críticos
7. **OCR offline**: Usar Tesseract para archivos confidenciales
