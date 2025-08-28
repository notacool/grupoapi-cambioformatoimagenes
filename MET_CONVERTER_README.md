# 📋 Conversor MET Metadata - Generador de Metadatos XML

## 🎯 Descripción

El **Conversor MET Metadata** es un nuevo módulo del sistema de conversión TIFF que genera archivos XML siguiendo el estándar **MET (Metadata Encoding and Transmission Standard)** de la Library of Congress. Este conversor crea metadatos detallados y estructurados para cada archivo TIFF procesado.

**Nueva Funcionalidad**: El sistema ahora también genera un **archivo METS del TIFF original** que documenta completamente el archivo fuente antes de la conversión, proporcionando trazabilidad completa desde el original hasta cada formato generado.

## 🔧 Características Principales

### ✨ Generación de Metadatos Completos
- **Metadatos de Imagen**: Dimensiones, DPI, formato, modo de color, compresión
- **Metadatos de Archivo**: Tamaño, fechas de creación/modificación, permisos
- **Metadatos de Procesamiento**: Información del conversor, configuración, historial
- **Verificación de Integridad**: Checksum MD5 para cada archivo

### 📊 Estándar METS Compliant
- Cumple con el estándar METS de la Library of Congress
- Estructura XML bien formada y validada
- Namespaces XML apropiados para interoperabilidad
- Esquemas XSD referenciados para validación

### 🎛️ Configuración Flexible
- Control granular sobre qué metadatos incluir
- Personalización de organización y creador
- Configuración de estándares de metadatos
- Opciones de procesamiento configurables

## 🚀 Casos de Uso

### 🏛️ Archivos y Bibliotecas
- **Preservación Digital**: Metadatos completos para archivos históricos
- **Catálogos**: Información estructurada para sistemas de búsqueda
- **Compliance**: Cumplimiento de estándares de metadatos institucionales

### 💼 Gestión Documental
- **Sistemas DMS**: Integración con sistemas de gestión documental
- **Workflows**: Trazabilidad completa del procesamiento
- **Auditoría**: Registro detallado de conversiones y modificaciones

### 🔍 Investigación y Análisis
- **Análisis de Imágenes**: Metadatos técnicos para investigación
- **Machine Learning**: Datos estructurados para entrenamiento de IA
- **Big Data**: Metadatos consistentes para análisis a gran escala

## 📁 Estructura de Salida

### Directorio de Salida
```
output_directory/
├── METS/                           # Archivo METS del TIFF original
│   └── TIFF.xml                   # ← Documentación completa del archivo fuente
├── met_metadata/                   # Metadatos individuales por archivo
│   ├── archivo1_MET.xml
│   ├── archivo2_MET.xml
│   └── archivo3_MET.xml
├── JPGHIGH/                        # JPGs de 400 DPI + metadatos consolidados
│   ├── archivo1_400dpi.jpg
│   └── JPGHIGH.xml                # ← Metadatos consolidados del formato
├── JPGLOW/                         # JPGs de 200 DPI + metadatos consolidados
│   ├── archivo1_200dpi.jpg
│   └── JPGLOW.xml                 # ← Metadatos consolidados del formato
└── PDF/                            # PDFs con OCR + metadatos consolidados
    ├── archivo1_EasyOCR.pdf
    └── PDF.xml                     # ← Metadatos consolidados del formato
```

### Tipos de Archivos XML Generados

#### 1. Archivo METS del TIFF Original (`TIFF.xml`)
- **Propósito**: Documentación completa del archivo fuente antes de la conversión
- **Contenido**: Metadatos técnicos, administrativos y de preservación del TIFF original
- **Ubicación**: `output_directory/METS/TIFF.xml`

#### 2. Metadatos Individuales (`{archivo}_MET.xml`)
- **Propósito**: Metadatos específicos de cada archivo TIFF procesado
- **Contenido**: Información detallada del archivo individual
- **Ubicación**: `output_directory/met_metadata/{archivo}_MET.xml`

#### 3. Metadatos Consolidados por Formato (`{formato}.xml`)
- **Propósito**: Metadatos consolidados que incluyen el TIFF original y los archivos convertidos
- **Contenido**: Trazabilidad completa desde el original hasta cada formato generado
- **Ubicación**: `output_directory/{formato}/{formato}.xml`

### Formato de Nombres
- **Metadatos individuales**: `{nombre_original}_MET.xml`
- **Metadatos consolidados**: `{formato}.xml` (ej: `JPGHIGH.xml`)
- **METS del TIFF original**: `TIFF.xml`

## ⚙️ Configuración

### Configuración Básica
```yaml
met_metadata:
  enabled: true
  include_image_metadata: true
  include_file_metadata: true
  include_processing_info: true
  metadata_standard: 'MET'
  organization: 'Mi Organización'
  creator: 'Sistema de Conversión'
```

### Opciones Avanzadas
```yaml
met_metadata:
  # Metadatos de imagen
  include_image_metadata: true
  
  # Metadatos del archivo
  include_file_metadata: true
  
  # Información de procesamiento
  include_processing_info: true
  
  # Estándar de metadatos
  metadata_standard: 'MET'
  
  # Información institucional
  organization: 'Biblioteca Nacional'
  creator: 'Conversor TIFF v2.0'
  
  # Configuración técnica
  include_exif: true
  include_checksum: true
  checksum_type: 'MD5'
```

## 📋 Estructura XML Generada

### Ejemplo de Archivo MET
```xml
<?xml version="1.0" encoding="utf-8"?>
<met xmlns="http://www.loc.gov/METS/"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd">
  
  <!-- Identificador del objeto -->
  <objid>documento_2024</objid>
  
  <!-- Información del agente -->
  <agent ROLE="CREATOR" TYPE="ORGANIZATION">
    <name>Mi Organización</name>
  </agent>
  
  <!-- Encabezado METS -->
  <metsHdr CREATEDATE="2024-01-15T10:30:00" LASTMODDATE="2024-01-15T10:30:00">
    <agent ROLE="CREATOR" TYPE="OTHER" OTHERTYPE="SOFTWARE">
      <name>Sistema de Conversión</name>
    </agent>
  </metsHdr>
  
  <!-- Sección de archivos -->
  <fileSec>
    <fileGrp USE="PRESERVATION">
      <file ID="FILE_documento_2024" MIMETYPE="image/tiff" SIZE="2048576" 
            CREATED="2024-01-15T09:00:00" CHECKSUM="a1b2c3d4..." CHECKSUMTYPE="MD5">
        
        <!-- Ubicación del archivo -->
        <FLocat xlink:href="/ruta/completa/documento_2024.tiff"/>
        
        <!-- Metadatos de imagen -->
        <imageInfo width="3000" height="2000" mode="RGB" format="TIFF" 
                   dpi_x="300" dpi_y="300" compression="LZW"/>
        
        <!-- Metadatos del archivo -->
        <fileInfo name="documento_2024.tiff" extension=".tiff" 
                  size_bytes="2048576" size_mb="1.95" 
                  created="2024-01-15T09:00:00" 
                  modified="2024-01-15T09:00:00" 
                  permissions="644"/>
        
        <!-- Información de procesamiento -->
        <processingInfo converter="METMetadataConverter" 
                        conversion_date="2024-01-15T10:30:00" 
                        metadata_standard="MET" version="1.0">
          <configuration include_image_metadata="True" 
                         include_file_metadata="True" 
                         include_processing_info="True"/>
        </processingInfo>
      </file>
    </fileGrp>
  </fileSec>
  
  <!-- Metadatos administrativos -->
  <amdSec>
    <techMD ID="TECHMD_documento_2024" MDTYPE="OTHER" OTHERMDTYPE="TECHNICAL">
      <mdWrap>
        <xmlData>
          <technicalInfo format="TIFF" conversionDate="2024-01-15T10:30:00" 
                         converter="Sistema de Conversión"/>
        </xmlData>
      </mdWrap>
    </techMD>
  </amdSec>
</met>
```

## 🧪 Pruebas y Uso

### Script de Prueba
```bash
# Ejecutar script de prueba
python test_met_converter.py

# Verificar archivos generados
ls -la test_output/met_metadata/
```

### Uso en Producción
```bash
# Convertir solo a metadatos MET
python main.py --input "imagenes/" --output "salida/" --formats met_metadata

# Convertir a todos los formatos incluyendo MET
python main.py --input "imagenes/" --output "salida/"

# Usar configuración personalizada
python main.py --input "imagenes/" --output "salida/" --config "config_met_example.yaml"
```

## 🔍 Validación y Verificación

### Validación XML
- **Formato**: XML bien formado con encoding UTF-8
- **Namespaces**: Declaraciones correctas de xmlns
- **Esquemas**: Referencias a esquemas XSD de METS
- **Indentación**: Formato legible y estructurado

### Verificación de Contenido
- **Metadatos Completos**: Todos los campos configurados están presentes
- **Checksums**: Verificación MD5 para integridad de archivos
- **Fechas**: Timestamps ISO 8601 para todas las fechas
- **Referencias**: Enlaces correctos a archivos originales

## 🚀 Integración con el Sistema

### Conversores Disponibles
1. **JPG 400 DPI**: Alta resolución para impresión
2. **JPG 200 DPI**: Resolución media para web
3. **PDF EasyOCR**: Texto buscable con OCR
4. **MET Metadata**: Metadatos XML estructurados ✨ **NUEVO**

### Flujo de Procesamiento
```
Archivo TIFF → Conversor MET → Archivo XML MET
     ↓              ↓              ↓
  Validación → Generación → Verificación
```

## 📚 Recursos y Referencias

### Estándares
- **METS**: [Library of Congress METS](http://www.loc.gov/standards/mets/)
- **XML**: [W3C XML Specification](https://www.w3.org/XML/)
- **ISO 8601**: [Formato de Fechas](https://en.wikipedia.org/wiki/ISO_8601)

### Herramientas de Validación
- **XML Validator**: [W3C Validator](https://validator.w3.org/)
- **METS Validator**: [Library of Congress](http://www.loc.gov/standards/mets/mets-validator.html)
- **Checksum MD5**: Verificación de integridad de archivos

## 🔮 Futuras Mejoras

### Funcionalidades Planificadas
- **Múltiples Estándares**: Soporte para Dublin Core, PREMIS
- **Metadatos Personalizados**: Campos específicos por organización
- **Validación Avanzada**: Verificación contra esquemas XSD
- **Integración con Bases de Datos**: Almacenamiento de metadatos
- **APIs REST**: Acceso programático a metadatos

### Optimizaciones Técnicas
- **Procesamiento Paralelo**: Generación concurrente de metadatos
- **Caché de Metadatos**: Almacenamiento temporal para archivos repetidos
- **Compresión**: Archivos XML comprimidos para ahorro de espacio
- **Indexación**: Búsqueda rápida en metadatos generados

## 📞 Soporte y Contacto

### Reportar Problemas
- **Issues**: [GitHub Issues](https://github.com/notacool/grupoapi-cambioformatoimagenes/issues)
- **Bug Reports**: Usar la plantilla de reporte de errores
- **Feature Requests**: Solicitudes de nuevas funcionalidades

### Contribuciones
- **Pull Requests**: Bienvenidos para mejoras y correcciones
- **Documentación**: Ayuda con ejemplos y casos de uso
- **Testing**: Pruebas en diferentes entornos y archivos

---

**🎉 ¡El Conversor MET Metadata está listo para generar metadatos profesionales y cumplir con estándares internacionales!**
