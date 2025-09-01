# 🗜️ Guía Completa de Compresión de PDF

## 📋 Índice
- [Introducción](#introducción)
- [Tipos de Compresión](#tipos-de-compresión)
- [Configuración](#configuración)
- [Niveles de Compresión](#niveles-de-compresión)
- [Optimización](#optimización)
- [Troubleshooting](#troubleshooting)
- [Ejemplos](#ejemplos)

---

## 🎯 Introducción

El **Sistema de Compresión Inteligente de PDF** está diseñado para reducir significativamente el tamaño de los archivos PDF generados, manteniendo la calidad visual y la funcionalidad de OCR. El sistema es **100% compatible con Docker** y no requiere dependencias externas del sistema.

### ✨ Características Principales

- **🐍 100% Python**: Sin dependencias de sistema como Ghostscript
- **🔧 Doble compresión**: Embebida durante la generación + post-procesamiento
- **⚙️ Altamente configurable**: Control granular sobre calidad y tamaño
- **🛡️ Fallback robusto**: Nunca falla, usa el archivo original si la compresión no funciona
- **📊 Transparente**: Reporta estadísticas de compresión en tiempo real

---

## 🔧 Tipos de Compresión

### 1. 📊 **Compresión Embebida** (Recomendada)

Se aplica **durante la generación del PDF** y es la más efectiva:

#### **Cómo Funciona:**
```python
# El sistema automáticamente:
1. Escala la imagen al DPI objetivo
2. Guarda como JPEG con calidad configurable
3. Optimiza la compresión JPEG
4. Embebe en el PDF con tamaño reducido
```

#### **Ventajas:**
- ✅ **Mayor reducción**: 40-70% del tamaño original
- ✅ **Sin dependencias**: Funciona en cualquier entorno
- ✅ **Rápida**: Se aplica durante la generación
- ✅ **Calidad predecible**: Control directo sobre DPI y calidad

#### **Configuración:**
```yaml
PDF:
  compression:
    target_dpi: 200        # DPI objetivo (menor = más compresión)
    image_quality: 85      # Calidad JPEG (menor = más compresión)
```

### 2. 🔧 **Post-Compresión**

Se aplica **después de crear el PDF** para optimización adicional:

#### **Herramientas Utilizadas:**
1. **pikepdf** (Preferida):
   - Compresión de streams
   - Eliminación de metadatos
   - Optimización de estructura

2. **pypdf** (Fallback):
   - Compresión básica
   - Reorganización de contenido

#### **Ventajas:**
- ✅ **Compresión adicional**: 10-30% más de reducción
- ✅ **Eliminación de metadatos**: Reduce información innecesaria
- ✅ **Optimización de estructura**: Mejora la organización interna

---

## ⚙️ Configuración

### **Configuración Básica**

```yaml
# Conversor PDF individual
PDF:
  compression:
    enabled: true                   # Habilitar compresión
    compression_level: "ebook"      # Nivel de compresión
    target_dpi: 200                 # DPI objetivo
    image_quality: 85               # Calidad JPEG (0-100)
    remove_metadata: true           # Eliminar metadatos
    fallback_on_error: true         # Usar original si falla
```

### **Configuración del Postconversor Consolidado**

```yaml
postconverters:
  consolidated_pdf:
    max_size_mb: 50                 # Tamaño máximo por PDF
    compression:
      enabled: true                 # Habilitar compresión
      compression_level: "ebook"    # Nivel de compresión
      target_dpi: 200               # DPI objetivo
      image_quality: 85             # Calidad JPEG
      remove_metadata: true         # Eliminar metadatos
      fallback_on_error: true       # Fallback automático
```

### **Parámetros Detallados**

| Parámetro | Tipo | Rango | Descripción |
|-----------|------|-------|-------------|
| `enabled` | bool | true/false | Habilitar/deshabilitar compresión |
| `compression_level` | string | screen/ebook/printer/prepress | Nivel de compresión predefinido |
| `target_dpi` | int | 72-600 | DPI objetivo para imágenes embebidas |
| `image_quality` | int | 1-100 | Calidad JPEG (100 = mejor calidad) |
| `remove_metadata` | bool | true/false | Eliminar metadatos del PDF |
| `fallback_on_error` | bool | true/false | Usar archivo original si falla |

---

## 📊 Niveles de Compresión

### **Configuraciones Predefinidas**

| Nivel | DPI | Calidad | Uso Recomendado | Reducción |
|-------|-----|---------|-----------------|-----------|
| **screen** | 72-150 | 70-80 | Web, visualización rápida | 60-80% |
| **ebook** | 150-200 | 80-90 | Lectura digital, archivo | 40-60% |
| **printer** | 200-300 | 85-95 | Impresión estándar | 20-40% |
| **prepress** | 300+ | 90-100 | Impresión profesional | 10-30% |

### **Personalización por Uso**

#### **💾 Máxima Compresión (Archivo/Web)**
```yaml
compression:
  compression_level: "screen"
  target_dpi: 150
  image_quality: 75
  remove_metadata: true
```
- **Reducción esperada**: 60-80%
- **Calidad**: Buena para visualización en pantalla

#### **📖 Lectura Digital (Recomendada)**
```yaml
compression:
  compression_level: "ebook"
  target_dpi: 200
  image_quality: 85
  remove_metadata: true
```
- **Reducción esperada**: 40-60%
- **Calidad**: Óptima para lectura en dispositivos

#### **🖨️ Impresión de Calidad**
```yaml
compression:
  compression_level: "printer"
  target_dpi: 300
  image_quality: 90
  remove_metadata: false
```
- **Reducción esperada**: 20-40%
- **Calidad**: Excelente para impresión

---

## 🎯 Optimización

### **Estrategias de Optimización**

#### **1. 📏 Optimización por Tamaño**
```yaml
# Para archivos muy grandes (>100MB TIFF)
compression:
  target_dpi: 150          # DPI bajo
  image_quality: 80        # Calidad media
  compression_level: "screen"
```

#### **2. 🖼️ Optimización por Calidad**
```yaml
# Para conservar máxima calidad
compression:
  target_dpi: 300          # DPI alto
  image_quality: 95        # Calidad alta
  compression_level: "prepress"
```

#### **3. ⚖️ Optimización Balanceada**
```yaml
# Balance óptimo (RECOMENDADA)
compression:
  target_dpi: 200          # DPI medio
  image_quality: 85        # Calidad buena
  compression_level: "ebook"
```

### **Ajuste Dinámico por Tamaño de Archivo**

```yaml
# Para archivos TIFF < 50MB
compression:
  target_dpi: 250
  image_quality: 90

# Para archivos TIFF 50-100MB
compression:
  target_dpi: 200
  image_quality: 85

# Para archivos TIFF > 100MB
compression:
  target_dpi: 150
  image_quality: 80
```

---

## 🔍 Troubleshooting

### **Problemas Comunes**

#### **1. ⚠️ "Compresión falló, usando PDF original"**

**Causa**: Error en pikepdf o pypdf durante post-compresión
**Solución**: 
```yaml
compression:
  fallback_on_error: true    # Ya configurado por defecto
```
**Resultado**: El sistema usa el PDF original (aún con compresión embebida)

#### **2. 📏 "PDF sigue siendo muy grande"**

**Causa**: Configuración de compresión muy conservadora
**Solución**:
```yaml
compression:
  target_dpi: 150            # Reducir DPI
  image_quality: 75          # Reducir calidad
  compression_level: "screen" # Usar nivel más agresivo
```

#### **3. 🖼️ "Calidad de imagen degradada"**

**Causa**: Configuración de compresión muy agresiva
**Solución**:
```yaml
compression:
  target_dpi: 250            # Aumentar DPI
  image_quality: 90          # Aumentar calidad
  compression_level: "printer" # Usar nivel más conservador
```

#### **4. 🐌 "Compresión muy lenta"**

**Causa**: Archivos muy grandes con configuración alta
**Solución**:
```yaml
compression:
  target_dpi: 200            # DPI moderado
  remove_metadata: true      # Eliminar metadatos
```

### **Diagnóstico de Compresión**

#### **Verificar Configuración**
```bash
python main.py --info
# Debe mostrar herramientas de compresión disponibles
```

#### **Modo Verbose**
```bash
python main.py --input "entrada" --verbose
# Muestra estadísticas de compresión en tiempo real
```

#### **Logs de Compresión**
Los logs incluyen información detallada:
```
🔄 Comprimiendo PDF: archivo.pdf (25.3 MB) -> ebook
✅ PDF comprimido: archivo.pdf (25.3 MB -> 12.7 MB, reducción: 49.8%)
```

---

## 📝 Ejemplos

### **Ejemplo 1: Configuración Básica**

```yaml
# config_basico.yaml
PDF:
  enabled: true
  compression:
    enabled: true
    compression_level: "ebook"
```

```bash
python main.py --input "documentos" --config config_basico.yaml
```

### **Ejemplo 2: Máxima Compresión**

```yaml
# config_maxima_compresion.yaml
PDF:
  compression:
    enabled: true
    compression_level: "screen"
    target_dpi: 150
    image_quality: 75

postconverters:
  consolidated_pdf:
    max_size_mb: 25  # Reducir tamaño máximo
    compression:
      enabled: true
      target_dpi: 150
      image_quality: 75
```

### **Ejemplo 3: Alta Calidad**

```yaml
# config_alta_calidad.yaml
PDF:
  compression:
    enabled: true
    compression_level: "prepress"
    target_dpi: 300
    image_quality: 95
    remove_metadata: false  # Conservar metadatos
```

### **Ejemplo 4: Compresión Deshabilitada**

```yaml
# config_sin_compresion.yaml
PDF:
  compression:
    enabled: false  # Deshabilitar completamente

postconverters:
  consolidated_pdf:
    compression:
      enabled: false  # Sin compresión en consolidados
```

---

## 📊 Métricas de Rendimiento

### **Resultados Típicos**

#### **Archivo de Prueba: documento.tiff (87 MB)**

| Configuración | PDF Original | PDF Comprimido | Reducción | Tiempo |
|---------------|--------------|----------------|-----------|---------|
| Sin compresión | 78.3 MB | 78.3 MB | 0% | 45s |
| screen (150 DPI, 75%) | 78.3 MB | 18.5 MB | 76% | 48s |
| ebook (200 DPI, 85%) | 78.3 MB | 28.2 MB | 64% | 47s |
| printer (300 DPI, 90%) | 78.3 MB | 45.1 MB | 42% | 46s |

### **Factores que Afectan la Compresión**

1. **Contenido de la imagen**:
   - Texto: Comprime muy bien
   - Fotografías: Compresión moderada
   - Diagramas: Compresión excelente

2. **DPI original**:
   - 400+ DPI: Mayor potencial de compresión
   - 200 DPI: Compresión moderada
   - <150 DPI: Poca mejora

3. **Tamaño del archivo**:
   - >50 MB: Excelente compresión
   - 10-50 MB: Buena compresión
   - <10 MB: Compresión limitada

---

## 🔧 Configuración Avanzada

### **Configuración por Tipo de Documento**

#### **Documentos de Texto**
```yaml
compression:
  target_dpi: 200
  image_quality: 80
  compression_level: "ebook"
```

#### **Documentos con Imágenes**
```yaml
compression:
  target_dpi: 250
  image_quality: 90
  compression_level: "printer"
```

#### **Planos/Diagramas Técnicos**
```yaml
compression:
  target_dpi: 300
  image_quality: 95
  compression_level: "prepress"
```

### **Configuración por Entorno**

#### **Desarrollo/Testing**
```yaml
compression:
  enabled: true
  compression_level: "screen"
  target_dpi: 150
  # Compresión rápida para pruebas
```

#### **Producción/Archivo**
```yaml
compression:
  enabled: true
  compression_level: "ebook"
  target_dpi: 200
  # Balance óptimo para archivo
```

#### **Distribución Web**
```yaml
compression:
  enabled: true
  compression_level: "screen"
  target_dpi: 150
  image_quality: 75
  # Máxima compresión para web
```

---

## 📞 Soporte

Para problemas específicos de compresión:

1. **Verificar logs**: Revisar mensajes de compresión en verbose
2. **Probar configuraciones**: Usar diferentes niveles de compresión
3. **Reportar issues**: Incluir configuración y logs de compresión

---

**💡 Tip**: La configuración `ebook` con `target_dpi: 200` y `image_quality: 85` ofrece el mejor balance entre tamaño y calidad para la mayoría de casos de uso.
