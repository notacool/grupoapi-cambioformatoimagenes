# 🚀 Guía del Desarrollador - Conversor TIFF

Esta guía explica cómo modificar, extender y mantener el proyecto Conversor TIFF para futuros desarrolladores.

## 📋 **Tabla de Contenidos**

1. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
2. [Estructura de Archivos](#estructura-de-archivos)
3. [Sistema de Salida con tqdm](#sistema-de-salida-con-tqdm)
4. [Cómo Agregar Nuevos Conversores](#cómo-agregar-nuevos-conversores)
5. [Cómo Modificar Conversores Existentes](#cómo-modificar-conversores-existentes)
6. [Sistema de Configuración](#sistema-de-configuración)
7. [Testing y Debugging](#testing-y-debugging)
8. [Flujo de Trabajo Git](#flujo-de-trabajo-git)
9. [Troubleshooting Común](#troubleshooting-común)

## 🏗️ **Arquitectura del Proyecto**

### **Patrón de Diseño**
El proyecto utiliza el **patrón Strategy** con conversores intercambiables:

```
BaseConverter (Interfaz)
├── JPGResolutionConverter (Estrategia JPG)
├── PDFEasyOCRConverter (Estrategia PDF + OCR)
└── METMetadataConverter (Estrategia Metadatos XML)
```

### **Componentes Principales**
- **`converter.py`**: Orquesta la conversión y gestiona conversores
- **`config_manager.py`**: Maneja configuración YAML
- **`file_processor.py`**: Procesa archivos y genera rutas de salida
- **`output_manager.py`**: Gestiona la salida usando tqdm
- **`converters/`**: Módulos de conversores específicos

## 📁 **Estructura de Archivos**

```
src/
├── converter.py              # Motor principal de conversión
├── config_manager.py         # Gestión de configuración
├── file_processor.py         # Procesamiento de archivos
├── output_manager.py         # Gestor de salida con tqdm
└── converters/
    ├── __init__.py          # Exporta conversores
    ├── base.py              # Clase base abstracta
    ├── jpg_resolution_converter.py    # Conversor JPG
    ├── pdf_easyocr_converter.py      # Conversor PDF + OCR
    └── met_metadata_converter.py     # Conversor Metadatos XML
```

## 🎯 **Sistema de Salida con tqdm**

### **¿Por qué tqdm?**

El proyecto utiliza **tqdm** para mantener la barra de progreso siempre visible en la parte inferior de la terminal. Esto es importante porque:

- **Mejora la experiencia del usuario**: La barra de progreso siempre está visible
- **Evita la confusión**: Los mensajes informativos no interfieren con el progreso
- **Mantiene el contexto**: El usuario puede ver tanto el progreso como la información

### **Gestor de Salida (OutputManager)**

El `OutputManager` centraliza toda la salida del sistema:

```python
from src.output_manager import output_manager

# Mensajes informativos (arriba de la barra de progreso)
output_manager.info("Procesando archivos...")
output_manager.success("Conversión completada")
output_manager.warning("Archivo ya existe")
output_manager.error("Error en la conversión")

# Formateo de información
output_manager.format_info("Archivos procesados", 10)
output_manager.format_list("Formatos", ["jpg_400", "pdf_easyocr"])
output_manager.section("RESUMEN")
output_manager.separator()
```

### **Integración con Conversores**

Todos los conversores deben usar el gestor de salida:

```python
from ..output_manager import output_manager

class MiConversor(BaseConverter):
    def convert(self, input_path: Path, output_path: Path) -> bool:
        try:
            # ... lógica de conversión ...
            output_manager.success(f"Convertido: {input_path.name}")
            return True
        except Exception as e:
            output_manager.error(f"Error: {str(e)}")
            return False
```

### **Barras de Progreso**

El sistema usa múltiples barras de progreso:

```python
# Barra principal de conversión
with tqdm(total=total_conversions, desc="Convirtiendo archivos", position=0) as main_pbar:
    output_manager.set_main_progress_bar(main_pbar)
    # ... procesamiento ...
```

## 🔧 **Cómo Agregar Nuevos Conversores**

### **Paso 1: Crear la Clase del Conversor**

Crea un nuevo archivo en `src/converters/` (ej: `bmp_converter.py`):

```python
from pathlib import Path
from typing import Dict, Any

from .base import BaseConverter
from ..output_manager import output_manager


class BMPConverter(BaseConverter):
    """Conversor de TIFF a BMP"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Configuración específica del conversor
        
    def convert(self, input_path: Path, output_path: Path) -> bool:
        try:
            # Validar entrada
            if not self.validate_input(input_path):
                output_manager.error(f"Archivo inválido: {input_path}")
                return False
                
            # Lógica de conversión
            # ...
            
            output_manager.success(f"Convertido: {input_path.name}")
            return True
            
        except Exception as e:
            output_manager.error(f"Error: {str(e)}")
            return False
            
    def get_file_extension(self) -> str:
        return ".bmp"
```

### **Paso 2: Agregar a la Inicialización**

Modifica `src/converter.py` para incluir el nuevo conversor:

```python
from .converters import (
    JPGResolutionConverter,
    PDFEasyOCRConverter,
    METMetadataConverter,
    BMPConverter,  # Nuevo conversor
)

def _initialize_converters(self) -> Dict[str, Any]:
    converters = {}
    
    # ... conversores existentes ...
    
    # BMP Converter
    if self.config_manager.is_format_enabled("bmp"):
        bmp_config = self.config_manager.get_format_config("bmp")
        converters["bmp"] = BMPConverter(bmp_config)
    
    return converters
```

### **Paso 3: Agregar Configuración**

Agrega la configuración en `config.yaml`:

```yaml
formats:
  bmp:
    enabled: true
    quality: 100
    compression: "none"
```

## 🔧 **Cómo Modificar Conversores Existentes**

### **Reglas Importantes**

1. **Siempre usa el gestor de salida**: Reemplaza `print()` por `output_manager.*()`
2. **Mantén la compatibilidad**: No cambies la interfaz pública sin documentar
3. **Maneja errores**: Usa try-catch y reporta errores con `output_manager.error()`
4. **Documenta cambios**: Actualiza docstrings y comentarios

### **Ejemplo de Modificación**

```python
# ANTES (incorrecto)
def convert(self, input_path: Path, output_path: Path) -> bool:
    print(f"Convirtiendo {input_path.name}...")  # ❌ No usar print
    # ... lógica ...
    print("✅ Conversión exitosa")  # ❌ No usar print
    return True

# DESPUÉS (correcto)
def convert(self, input_path: Path, output_path: Path) -> bool:
    output_manager.info(f"Convirtiendo {input_path.name}...")  # ✅ Usar output_manager
    # ... lógica ...
    output_manager.success("Conversión exitosa")  # ✅ Usar output_manager
    return True
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

met_metadata:
  enabled: true
  generate_all_met: false  # Archivos consolidados por formato
```

### **Acceso a Configuración**

```python
# En conversores
quality = self.config.get("quality", 90)  # Valor por defecto
dpi = self.config.get("dpi", 200)

# En el conversor principal
if self.config_manager.is_format_enabled("jpg_400"):
    # El formato está habilitado
```

## 🧪 **Testing y Debugging**

### **Ejecutar Tests**

```bash
# Tests generales
python test_converter.py

# Tests específicos
python test_met_converter.py
python test_consolidated_met.py
```

### **Modo Verbose**

```bash
python main.py --input "entrada/" --output "salida/" --verbose
```

### **Debugging**

1. **Usa el modo verbose** para ver información detallada
2. **Revisa los logs** del gestor de salida
3. **Verifica la configuración** con `--info`
4. **Usa breakpoints** en conversores específicos

## 🔄 **Flujo de Trabajo Git**

### **Branches**

- **`main`**: Código estable y probado
- **`develop`**: Desarrollo activo
- **`feature/*`**: Nuevas funcionalidades
- **`hotfix/*`**: Correcciones urgentes

### **Commits**

```
feat: agregar conversor BMP
fix: corregir error en generación de MET
docs: actualizar guía del desarrollador
refactor: usar output_manager en conversores
```

## 🚨 **Troubleshooting Común**

### **Problema: La barra de progreso no se muestra**

**Solución**: Verifica que estés usando `output_manager.*()` en lugar de `print()`

### **Problema: Mensajes aparecen en el lugar incorrecto**

**Solución**: Asegúrate de que `output_manager.set_main_progress_bar()` esté configurado

### **Problema: Conversor no se inicializa**

**Solución**: Verifica la configuración en `config.yaml` y los imports en `__init__.py`

### **Problema: Error de permisos**

**Solución**: Verifica permisos de escritura en el directorio de salida

## 📚 **Recursos Adicionales**

- **Documentación de tqdm**: https://tqdm.github.io/
- **Guía de PIL/Pillow**: https://pillow.readthedocs.io/
- **Documentación de EasyOCR**: https://github.com/JaidedAI/EasyOCR
- **Estándar METS**: https://www.loc.gov/standards/mets/

## 🤝 **Contribuir**

1. **Fork** el repositorio
2. **Crea** una rama para tu feature
3. **Implementa** los cambios siguiendo esta guía
4. **Testea** tu código
5. **Envía** un pull request

### **Estándares de Código**

- **Python 3.8+**: Usa type hints y f-strings
- **PEP 8**: Sigue las convenciones de estilo
- **Docstrings**: Documenta todas las funciones públicas
- **Tests**: Agrega tests para nuevas funcionalidades
- **Output Manager**: Siempre usa `output_manager` en lugar de `print()`

---

**Nota**: Esta guía se actualiza regularmente. Si encuentras inconsistencias o tienes sugerencias, por favor abre un issue o envía un pull request.
